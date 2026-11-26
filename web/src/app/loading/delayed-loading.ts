import { InjectionToken, Signal, effect, inject, signal } from '@angular/core';

/**
 * How long a load must last before a skeleton appears. Local loads take milliseconds, so they
 * never flash one; a Vercel cold start takes longer, and then the skeleton shows (D-055).
 */
export const SKELETON_DELAY_MS = new InjectionToken<number>('SKELETON_DELAY_MS', {
  factory: () => 300,
});

/** True once `isLoading` has stayed true for the delay. Call it in an injection context. */
export function delayedLoading(isLoading: () => boolean): Signal<boolean> {
  const delay = inject(SKELETON_DELAY_MS);
  const slow = signal(false);
  effect((onCleanup) => {
    if (!isLoading()) {
      slow.set(false);
      return;
    }
    const timer = setTimeout(() => slow.set(true), delay);
    onCleanup(() => clearTimeout(timer));
  });
  return slow.asReadonly();
}
