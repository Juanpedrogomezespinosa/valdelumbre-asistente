import { HttpErrorResponse } from '@angular/common/http';

/** Resources wrap non-Error failures such as HttpErrorResponse and keep the original as `cause`. */
export function isNotFound(error: unknown): boolean {
  const original = error instanceof Error && error.cause ? error.cause : error;
  return original instanceof HttpErrorResponse && original.status === 404;
}
