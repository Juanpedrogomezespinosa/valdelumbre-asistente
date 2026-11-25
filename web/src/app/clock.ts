import { InjectionToken } from '@angular/core';

/** The current moment, injectable so tests do not depend on when they run. */
export const CLOCK = new InjectionToken<() => Date>('CLOCK', {
  providedIn: 'root',
  factory: () => () => new Date(),
});
