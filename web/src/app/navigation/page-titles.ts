import { Injectable, Provider, effect, inject, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterStateSnapshot, TitleStrategy } from '@angular/router';
import { I18n } from '../i18n/i18n';
import { PageKey, TEXTS } from '../i18n/texts';

/** Lets a page with its own name (a point of interest) title the tab with it. */
@Injectable({ providedIn: 'root' })
export class PageName {
  readonly current = signal<string | null>(null);
}

/**
 * Routes declare a page key as their `title`; the document title is that page's name in the
 * active language, or the name a page sets, and follows language changes (D-027).
 */
@Injectable()
class PageTitleStrategy extends TitleStrategy {
  private readonly i18n = inject(I18n);
  private readonly title = inject(Title);
  private readonly pageName = inject(PageName);
  private readonly page = signal<PageKey | null>(null);

  constructor() {
    super();
    effect(() => {
      const page = this.page();
      const texts = this.i18n.texts();
      const name = this.pageName.current() ?? (page ? texts.pages[page] : null);
      if (name) {
        this.title.setTitle(`${name} · ${texts.siteName}`);
      }
    });
  }

  override updateTitle(snapshot: RouterStateSnapshot): void {
    const key = this.buildTitle(snapshot);
    this.pageName.current.set(null);
    this.page.set(key && key in TEXTS.es.pages ? (key as PageKey) : null);
  }
}

export function providePageTitles(): Provider {
  return { provide: TitleStrategy, useClass: PageTitleStrategy };
}
