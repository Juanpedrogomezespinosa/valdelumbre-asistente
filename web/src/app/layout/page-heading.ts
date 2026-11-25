import { Component } from '@angular/core';

/** The page <h1>. Focusable from script (not from Tab) so navigation can move focus to it. */
@Component({
  selector: 'app-page-heading',
  template: `<h1 tabindex="-1" class="mb-4 font-display text-4xl font-semibold sm:text-5xl">
    <ng-content />
  </h1>`,
})
export class PageHeading {}
