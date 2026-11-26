import { Component, computed, input } from '@angular/core';

/** Placeholder cards with the card's shape. Decorative: the status region says it is loading. */
@Component({
  selector: 'app-skeleton-cards',
  template: `
    <ul data-skeleton aria-hidden="true" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      @for (slot of slots(); track slot) {
        <li class="flex h-36 flex-col rounded-2xl border border-line bg-surface p-5 shadow-sm">
          <span class="mb-2 h-3 w-20 rounded bg-sunk motion-safe:animate-pulse"></span>
          <span class="h-5 w-3/4 rounded bg-sunk motion-safe:animate-pulse"></span>
          <span class="mt-auto flex gap-2">
            <span class="h-7 w-20 rounded-full bg-sunk motion-safe:animate-pulse"></span>
            <span class="h-7 w-24 rounded-full bg-sunk motion-safe:animate-pulse"></span>
            <span class="h-7 w-14 rounded-full bg-sunk motion-safe:animate-pulse"></span>
          </span>
        </li>
      }
    </ul>
  `,
})
export class SkeletonCards {
  readonly count = input(6);
  protected readonly slots = computed(() => Array.from({ length: this.count() }, (_, i) => i));
}
