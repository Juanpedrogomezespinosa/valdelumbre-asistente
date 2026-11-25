import { Component, ElementRef, inject, viewChild } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { I18n } from './i18n/i18n';
import { LanguageSwitcher } from './layout/language-switcher';
import { ThemeToggle } from './layout/theme-toggle';
import { HeadingFocus } from './navigation/heading-focus';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, LanguageSwitcher, ThemeToggle],
  templateUrl: './app.html',
})
export class App {
  protected readonly i18n = inject(I18n);
  private readonly main = viewChild.required<ElementRef<HTMLElement>>('main');

  constructor() {
    inject(HeadingFocus).watch();
  }

  // With <base href="/">, a bare "#main" link would navigate to the home page instead.
  protected skipToMain(event: Event): void {
    event.preventDefault();
    this.main().nativeElement.focus();
  }
}
