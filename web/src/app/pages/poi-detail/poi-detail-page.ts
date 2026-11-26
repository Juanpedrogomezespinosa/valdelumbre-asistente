import { Component, computed, effect, inject } from '@angular/core';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { map } from 'rxjs';
import { I18n } from '../../i18n/i18n';
import { delayedLoading } from '../../loading/delayed-loading';
import { SkeletonDetail } from '../../loading/skeleton-detail';
import { PageHeading } from '../../layout/page-heading';
import { PageName } from '../../navigation/page-titles';
import { ServedText, Slot } from '../../pois/poi';
import { accessibilityText, openNowText } from '../../pois/poi-labels';
import { PoisService } from '../../pois/pois-service';
import { isNotFound } from '../../http-error';
import { slotText } from '../../pois/schedule-text';
import { CategoryIllustration } from '../../pois/category-illustration';
import { NO_FILTERS } from '../../pois/poi-filters';
import { nearby } from '../../pois/nearby';
import { LANDMARK_ID, relativeLocation } from '../../pois/relative-location';
import { VillageMap } from '../../pois/village-map';

const NEARBY_COUNT = 3;

@Component({
  selector: 'app-poi-detail-page',
  imports: [PageHeading, RouterLink, CategoryIllustration, SkeletonDetail, VillageMap],
  templateUrl: './poi-detail-page.html',
})
export class PoiDetailPage {
  protected readonly i18n = inject(I18n);
  private readonly pois = inject(PoisService);
  private readonly pageName = inject(PageName);

  private readonly id = toSignal(
    inject(ActivatedRoute).paramMap.pipe(map((params) => params.get('id') ?? '')),
    { requireSync: true },
  );

  protected readonly poi = rxResource({
    params: () => ({ id: this.id(), language: this.i18n.language() }),
    stream: ({ params }) => this.pois.get(params.id, params.language),
  });

  /** The whole catalogue, for the map and the square the location is measured from. */
  protected readonly slowLoading = delayedLoading(() => this.poi.isLoading());

  protected readonly catalogue = rxResource({
    params: () => ({ language: this.i18n.language() }),
    stream: ({ params }) => this.pois.list(NO_FILTERS, params.language),
  });

  /** "A 120 m al oeste de Plaza Mayor"; nothing for the square itself. */
  protected readonly location = computed(() => {
    if (!this.poi.hasValue()) {
      return null;
    }
    const place = this.poi.value();
    const texts = this.i18n.texts();
    if (!place.coordenadas) {
      return texts.location.unknown;
    }
    const landmark = this.catalogue.hasValue()
      ? this.catalogue.value().find((poi) => poi.id === LANDMARK_ID)
      : undefined;
    if (!landmark?.coordenadas || landmark.id === place.id) {
      return null;
    }
    return relativeLocation(
      place.coordenadas,
      { name: landmark.nombre.texto, coordinates: landmark.coordenadas },
      texts,
    );
  });

  protected readonly nearbyPlaces = computed(() =>
    this.poi.hasValue() && this.catalogue.hasValue()
      ? nearby(this.poi.value(), this.catalogue.value(), NEARBY_COUNT, this.i18n.texts())
      : [],
  );

  /** Empty once loaded: the region stays in the page so later changes are still announced. */
  protected readonly status = computed(() => {
    const texts = this.i18n.texts().poiDetail;
    if (this.poi.isLoading()) {
      return texts.loading;
    }
    const error = this.poi.error();
    if (error) {
      return isNotFound(error) ? texts.notFound : texts.loadError;
    }
    return '';
  });

  constructor() {
    effect(() => {
      this.pageName.current.set(this.poi.hasValue() ? this.poi.value().nombre.texto : null);
    });
  }

  protected accessibility(accessible: boolean | null): string {
    return accessibilityText(accessible, this.i18n.texts());
  }

  protected openNow(open: boolean | null): string {
    return openNowText(open, this.i18n.texts());
  }

  protected slotDescription(slot: Slot): string {
    return slotText(slot, this.i18n.texts());
  }

  /** A text served in another language than the page's gets its own `lang` (D-015). */
  protected foreignLanguage(text: ServedText): string | null {
    return text.idioma === this.i18n.language() ? null : text.idioma;
  }
}
