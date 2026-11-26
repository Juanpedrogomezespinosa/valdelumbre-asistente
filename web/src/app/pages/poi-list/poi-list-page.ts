import { Component, computed, inject } from '@angular/core';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { map } from 'rxjs';
import { I18n } from '../../i18n/i18n';
import { delayedLoading } from '../../loading/delayed-loading';
import { SkeletonCards } from '../../loading/skeleton-cards';
import { PageHeading } from '../../layout/page-heading';
import { CATEGORIES, isCategory } from '../../pois/poi';
import { PoiCard } from '../../pois/poi-card';
import { PoiFilters, filtersFromQuery, filtersToQuery } from '../../pois/poi-filters';
import { PoisService } from '../../pois/pois-service';
import { VillageMap } from '../../pois/village-map';

type ListView = 'list' | 'map';
const MAP_VIEW = 'mapa';

@Component({
  selector: 'app-poi-list-page',
  imports: [PageHeading, PoiCard, SkeletonCards, VillageMap],
  templateUrl: './poi-list-page.html',
})
export class PoiListPage {
  protected readonly i18n = inject(I18n);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly pois = inject(PoisService);

  protected readonly categories = CATEGORIES;
  protected readonly filters = toSignal(this.route.queryParamMap.pipe(map(filtersFromQuery)), {
    requireSync: true,
  });

  /** List or map; kept in the URL (`?vista=mapa`) like the filters, so it can be shared. */
  protected readonly view = toSignal(
    this.route.queryParamMap.pipe(
      map((query): ListView => (query.get('vista') === MAP_VIEW ? 'map' : 'list')),
    ),
    { requireSync: true },
  );

  protected readonly results = rxResource({
    params: () => ({ filters: this.filters(), language: this.i18n.language() }),
    stream: ({ params }) => this.pois.list(params.filters, params.language),
  });

  protected readonly slowLoading = delayedLoading(() => this.results.isLoading());

  /** Announced politely after every change, so the result count is heard (role="status"). */
  protected readonly status = computed(() => {
    const texts = this.i18n.texts().poiList;
    if (this.results.isLoading()) {
      return texts.loading;
    }
    if (this.results.error()) {
      return texts.loadError;
    }
    const count = this.results.hasValue() ? this.results.value().length : 0;
    return count === 0 ? texts.none : texts.found(count);
  });

  protected chooseCategory(event: Event): void {
    const value = selectedValue(event);
    this.apply({ category: isCategory(value) ? value : null });
  }

  protected chooseAccessibility(event: Event): void {
    const value = selectedValue(event);
    this.apply({ accessible: value === 'true' ? true : value === 'false' ? false : null });
  }

  protected toggleOpenNow(event: Event): void {
    this.apply({ openNow: (event.target as HTMLInputElement).checked });
  }

  protected showView(view: ListView): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { vista: view === 'map' ? MAP_VIEW : null },
      queryParamsHandling: 'merge',
    });
  }

  private apply(change: Partial<PoiFilters>): void {
    void this.router.navigate([], {
      relativeTo: this.route,
      queryParams: filtersToQuery({ ...this.filters(), ...change }),
      queryParamsHandling: 'merge',
    });
  }
}

function selectedValue(event: Event): string {
  return (event.target as HTMLSelectElement).value;
}
