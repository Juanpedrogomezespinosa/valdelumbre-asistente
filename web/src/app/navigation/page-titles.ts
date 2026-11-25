import { Injectable, Provider, effect, inject, signal } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { RouterStateSnapshot, TitleStrategy } from '@angular/router';
import { I18n } from '../i18n/i18n';
import { PageKey, TEXTS } from '../i18n/texts';

/**
 * Routes declare a page key as their `title`; the document title is that page's name in the
 * active language, and follows language changes (D-027).
 */
@Injectable()
class PageTitleStrategy extends TitleStrategy {
  private readonly i18n = inject(I18n);
  private readonly title = inject(Title);
  private readonly page = signal<PageKey | null>(null);

  constructor() {
    super();
    effect(() => {
      const page = this.page();
      const texts = this.i18n.texts();
      if (page) {
        this.title.setTitle(`${texts.pages[page]} · ${texts.siteName}`);
      }
    });
  }

  override updateTitle(snapshot: RouterStateSnapshot): void {
    const key = this.buildTitle(snapshot);
    this.page.set(key && key in TEXTS.es.pages ? (key as PageKey) : null);
  }
}

export function providePageTitles(): Provider {
  return { provide: TitleStrategy, useClass: PageTitleStrategy };
}
