import { Component, inject } from '@angular/core';
import { I18n } from '../i18n/i18n';
import { LANGUAGES, LANGUAGE_NAMES, isLanguage } from '../i18n/language';

@Component({
  selector: 'app-language-switcher',
  template: `
    <label for="language" class="mr-2 text-sm text-muted">{{ i18n.texts().languageLabel }}</label>
    <select
      id="language"
      class="rounded border border-control-border bg-surface px-2 py-1 text-text"
      (change)="choose($event)"
    >
      @for (language of languages; track language) {
        <option [value]="language" [attr.lang]="language" [selected]="language === i18n.language()">
          {{ names[language] }}
        </option>
      }
    </select>
  `,
})
export class LanguageSwitcher {
  protected readonly i18n = inject(I18n);
  protected readonly languages = LANGUAGES;
  protected readonly names = LANGUAGE_NAMES;

  protected choose(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    if (isLanguage(value)) {
      this.i18n.use(value);
    }
  }
}
