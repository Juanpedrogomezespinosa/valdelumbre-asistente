import { convertToParamMap } from '@angular/router';
import { NO_FILTERS, filtersFromQuery, filtersToQuery } from './poi-filters';

describe('POI filters in the URL', () => {
  it('reads every filter from the query string', () => {
    const query = convertToParamMap({ categoria: 'museo', accesible: 'true', abierto: 'ahora' });

    expect(filtersFromQuery(query)).toEqual({
      category: 'museo',
      accessible: true,
      openNow: true,
    });
  });

  it('reads accesible=false as "not accessible", not as "any"', () => {
    expect(filtersFromQuery(convertToParamMap({ accesible: 'false' })).accessible).toBe(false);
  });

  it('ignores values it does not understand instead of failing', () => {
    const query = convertToParamMap({ categoria: 'playa', accesible: 'quizas', abierto: 'x' });

    expect(filtersFromQuery(query)).toEqual(NO_FILTERS);
  });

  it('writes only the active filters, so an empty filter leaves no trace in the URL', () => {
    expect(filtersToQuery({ category: null, accessible: false, openNow: false })).toEqual({
      categoria: null,
      accesible: 'false',
      abierto: null,
    });
  });
});
