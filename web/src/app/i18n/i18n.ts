import { DOCUMENT, Injectable, computed, effect, inject, signal } from '@angular/core';
import { Language, isLanguage } from './language';
import { TEXTS } from './texts';

const STORAGE_KEY = 'valdelumbre.idioma';

/** Interface texts in the active language (D-028). The same language is sent to the API. */
@Injectable({ providedIn: 'root' })
export class I18n {
  private readonly document = inject(DOCUMENT);
  private readonly current = signal<Language>(storedLanguage() ?? 'es');

  readonly language = this.current.asReadonly();
  readonly texts = computed(() => TEXTS[this.current()]);

  constructor() {
    effect(() => {
      this.document.documentElement.lang = this.current();
    });
  }

  use(language: Language): void {
    this.current.set(language);
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch {
      // Storage can be unavailable (private mode); the choice then lasts for the session only.
    }
  }
}

function storedLanguage(): Language | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return isLanguage(stored) ? stored : null;
  } catch {
    return null;
  }
}
