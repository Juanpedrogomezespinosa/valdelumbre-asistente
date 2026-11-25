import { Component, computed, inject } from '@angular/core';
import { I18n } from '../i18n/i18n';
import { ThemePreference } from './theme-preference';

/** A pressed/not-pressed button: the name stays the same and the state is announced. */
@Component({
  selector: 'app-theme-toggle',
  template: `
    <button
      type="button"
      class="flex size-10 items-center justify-center rounded-full border border-control-border bg-surface text-text hover:border-primary hover:text-primary"
      [attr.aria-pressed]="dark()"
      [attr.aria-label]="i18n.texts().darkMode"
      (click)="theme.toggle()"
    >
      <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" class="size-5 fill-current">
        @if (dark()) {
          <circle cx="12" cy="12" r="4.5" />
          <path
            d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3M4.6 4.6l2.1 2.1M17.3 17.3l2.1 2.1M4.6 19.4l2.1-2.1M17.3 6.7l2.1-2.1"
            class="fill-none stroke-current"
            stroke-width="2"
            stroke-linecap="round"
          />
        } @else {
          <path d="M20.5 14.6A8.5 8.5 0 0 1 9.4 3.5a8.5 8.5 0 1 0 11.1 11.1z" />
        }
      </svg>
    </button>
  `,
})
export class ThemeToggle {
  protected readonly i18n = inject(I18n);
  protected readonly theme = inject(ThemePreference);
  protected readonly dark = computed(() => this.theme.current() === 'dark');
}
