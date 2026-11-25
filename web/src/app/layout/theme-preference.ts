import { DOCUMENT, Injectable, computed, effect, inject, signal } from '@angular/core';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'valdelumbre.tema';
const DARK_QUERY = '(prefers-color-scheme: dark)';

/**
 * Light or dark theme (D-045). Follows the system until the visitor chooses; the choice is
 * remembered and written as `data-theme` on <html>, which sets the CSS `color-scheme`.
 */
@Injectable({ providedIn: 'root' })
export class ThemePreference {
  private readonly document = inject(DOCUMENT);
  private readonly chosen = signal<Theme | null>(storedTheme());
  private readonly system = signal<Theme>('light');

  readonly current = computed(() => this.chosen() ?? this.system());

  constructor() {
    this.followSystem();
    effect(() => {
      const chosen = this.chosen();
      if (chosen) {
        this.document.documentElement.dataset['theme'] = chosen;
      }
    });
  }

  toggle(): void {
    const next: Theme = this.current() === 'dark' ? 'light' : 'dark';
    this.chosen.set(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Storage can be unavailable (private mode); the choice then lasts for the session only.
    }
  }

  private followSystem(): void {
    // matchMedia is missing in some environments (tests, very old browsers): stay on light.
    const query = this.document.defaultView?.matchMedia?.(DARK_QUERY);
    if (!query) {
      return;
    }
    this.system.set(query.matches ? 'dark' : 'light');
    query.addEventListener('change', (event) => this.system.set(event.matches ? 'dark' : 'light'));
  }
}

function storedTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'light' || stored === 'dark' ? stored : null;
  } catch {
    return null;
  }
}
