import { HttpErrorResponse } from '@angular/common/http';

/** Resources wrap non-Error failures such as HttpErrorResponse and keep the original as `cause`. */
function httpErrorIn(error: unknown): HttpErrorResponse | null {
  const original = error instanceof Error && error.cause ? error.cause : error;
  return original instanceof HttpErrorResponse ? original : null;
}

export function isNotFound(error: unknown): boolean {
  return httpErrorIn(error)?.status === 404;
}

/** The message the API wrote for the user, already in the requested language (D-039). */
export function apiErrorDetail(error: unknown): string | null {
  const detail: unknown = httpErrorIn(error)?.error?.detail;
  return typeof detail === 'string' ? detail : null;
}
