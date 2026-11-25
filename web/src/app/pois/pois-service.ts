import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { CLOCK } from '../clock';
import { Language } from '../i18n/language';
import { Poi } from './poi';
import { PoiFilters } from './poi-filters';

@Injectable({ providedIn: 'root' })
export class PoisService {
  private readonly http = inject(HttpClient);
  private readonly now = inject(CLOCK);

  list(filters: PoiFilters, language: Language): Observable<Poi[]> {
    let params = new HttpParams().set('idioma', language);
    if (filters.category) {
      params = params.set('categoria', filters.category);
    }
    if (filters.accessible !== null) {
      params = params.set('accesible', filters.accessible);
    }
    if (filters.openNow) {
      // A full date and time with its zone: the API converts it to the village's time (D-012).
      params = params.set('abierto_en', this.now().toISOString());
    }
    return this.http.get<Poi[]>('/api/pois', { params });
  }

  get(id: string, language: Language): Observable<Poi> {
    return this.http.get<Poi>(`/api/pois/${encodeURIComponent(id)}`, {
      params: { idioma: language },
    });
  }
}
