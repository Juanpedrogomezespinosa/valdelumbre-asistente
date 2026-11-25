import { DOCUMENT, Injectable, Injector, afterNextRender, inject } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs';

/**
 * After moving to another page, focus its <h1> so screen readers announce it (D-027). The
 * first load is left alone (the reader starts at the top as usual), and so are changes that
 * only touch the query string, such as filters.
 */
@Injectable({ providedIn: 'root' })
export class HeadingFocus {
  private readonly router = inject(Router);
  private readonly injector = inject(Injector);
  private readonly document = inject(DOCUMENT);

  watch(): void {
    this.router.events
      .pipe(filter((event): event is NavigationEnd => event instanceof NavigationEnd))
      .subscribe((event) => {
        const previous = this.router.lastSuccessfulNavigation()?.previousNavigation?.finalUrl;
        // Only a new page moves the focus: changing a filter or the list/map view keeps the
        // keyboard user where they were.
        if (
          previous &&
          this.pathOf(this.router.serializeUrl(previous)) !== this.pathOf(event.urlAfterRedirects)
        ) {
          afterNextRender(() => this.focusHeading(), { injector: this.injector });
        }
      });
  }

  private pathOf(url: string): string {
    return url.split(/[?#]/)[0];
  }

  private focusHeading(): void {
    this.document.querySelector<HTMLElement>('main h1')?.focus();
  }
}
