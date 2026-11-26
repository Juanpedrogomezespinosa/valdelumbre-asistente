import { Component } from '@angular/core';

/** Placeholder with the detail page's shape. Decorative: the status region says it is loading. */
@Component({
  selector: 'app-skeleton-detail',
  template: `
    <div data-skeleton aria-hidden="true">
      <div class="mb-5 h-40 rounded-3xl bg-sunk motion-safe:animate-pulse"></div>
      <div class="grid gap-5 md:grid-cols-2">
        <div class="rounded-2xl border border-line bg-surface p-6 shadow-sm md:col-span-2 sm:p-8">
          <span class="mb-4 block h-6 w-40 rounded bg-sunk motion-safe:animate-pulse"></span>
          <span class="mb-2 block h-4 w-full rounded bg-sunk motion-safe:animate-pulse"></span>
          <span class="block h-4 w-2/3 rounded bg-sunk motion-safe:animate-pulse"></span>
        </div>
        <div class="h-48 rounded-2xl bg-sunk motion-safe:animate-pulse"></div>
        <div class="h-48 rounded-2xl bg-sunk motion-safe:animate-pulse"></div>
      </div>
    </div>
  `,
})
export class SkeletonDetail {}
