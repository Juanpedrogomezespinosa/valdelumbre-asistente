import { Component, computed, effect, inject } from '@angular/core';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { map } from 'rxjs';
import { I18n } from '../../i18n/i18n';
import { PageHeading } from '../../layout/page-heading';
import { PageName } from '../../navigation/page-titles';
import { ServedText, Slot } from '../../pois/poi';
import { accessibilityText, openNowText } from '../../pois/poi-labels';
import { PoisService } from '../../pois/pois-service';
import { isNotFound } from '../../pois/not-found-error';
import { slotText } from '../../pois/schedule-text';

@Component({
  selector: 'app-poi-detail-page',
  imports: [PageHeading, RouterLink],
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
