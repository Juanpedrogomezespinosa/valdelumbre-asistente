import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Language } from '../i18n/language';

/** The API contract of POST /preguntar, exactly as the brief defines it (D-042). */
export interface AssistantAnswer {
  respuesta: string;
  ids: string[];
}

@Injectable({ providedIn: 'root' })
export class AssistantService {
  private readonly http = inject(HttpClient);

  ask(question: string, language: Language): Observable<AssistantAnswer> {
    return this.http.post<AssistantAnswer>('/api/preguntar', {
      pregunta: question,
      idioma: language,
    });
  }
}
