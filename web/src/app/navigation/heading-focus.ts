import { DOCUMENT, Injectable, Injector, afterNextRender, inject } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

/**
 * After each in-app navigation, focus the page's <h1> so screen readers announce the new
 * page (D-027). The first load is left alone: the reader starts at the top as usual.
 */
@Injectable({ providedIn: 'root' })
export class HeadingFocus {
  private readonly router = inject(Router);
  private readonly injector = inject(Injector);
  private readonly document = inject(DOCUMENT);

  watch(): void {
    this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe(() => {
      if (this.router.lastSuccessfulNavigation()?.previousNavigation) {
        afterNextRender(() => this.focusHeading(), { injector: this.injector });
      }
    });
  }

  private focusHeading(): void {
    this.document.querySelector<HTMLElement>('main h1')?.focus();
  }
}
