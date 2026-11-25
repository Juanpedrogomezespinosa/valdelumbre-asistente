import { ParamMap, Params } from '@angular/router';
import { Category, isCategory } from './poi';

export interface PoiFilters {
  category: Category | null;
  /** null = any; false really means "not accessible" (D-008). */
  accessible: boolean | null;
  openNow: boolean;
}

export const NO_FILTERS: PoiFilters = { category: null, accessible: null, openNow: false };

const OPEN_NOW = 'ahora';

/** Filters live in the URL so they can be shared and survive a reload (D-027). */
export function filtersFromQuery(query: ParamMap): PoiFilters {
  const category = query.get('categoria');
  const accessible = query.get('accesible');
  return {
    category: isCategory(category) ? category : null,
    accessible: accessible === 'true' ? true : accessible === 'false' ? false : null,
    openNow: query.get('abierto') === OPEN_NOW,
  };
}

/** null removes the parameter from the URL. */
export function filtersToQuery(filters: PoiFilters): Params {
  return {
    categoria: filters.category,
    accesible: filters.accessible === null ? null : String(filters.accessible),
    abierto: filters.openNow ? OPEN_NOW : null,
  };
}
