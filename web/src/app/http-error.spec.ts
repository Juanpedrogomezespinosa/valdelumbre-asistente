import { HttpErrorResponse } from '@angular/common/http';
import { apiErrorDetail, isNotFound } from './http-error';

const notFound = new HttpErrorResponse({ status: 404, error: { detail: 'No existe' } });
const invalid = new HttpErrorResponse({ status: 422, error: { detail: 'La pregunta no puede…' } });

describe('HTTP errors seen through a resource', () => {
  it('finds the original response inside the error a resource wraps', () => {
    const wrapped = new Error('Resource is in an error state', { cause: notFound });

    expect(isNotFound(wrapped)).toBe(true);
    expect(isNotFound(notFound)).toBe(true);
    expect(isNotFound(new Error('other'))).toBe(false);
  });

  it('gives the localized detail the API sent with a 422', () => {
    expect(apiErrorDetail(new Error('x', { cause: invalid }))).toBe('La pregunta no puede…');
    expect(apiErrorDetail(new HttpErrorResponse({ status: 0 }))).toBeNull();
  });
});
