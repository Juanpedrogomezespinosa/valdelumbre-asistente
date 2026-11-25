export type Language = 'es' | 'en';

export const LANGUAGES: readonly Language[] = ['es', 'en'];

/** Each language is named in itself, so the selector reads the same in any interface language. */
export const LANGUAGE_NAMES: Record<Language, string> = { es: 'Español', en: 'English' };

export function isLanguage(value: unknown): value is Language {
  return LANGUAGES.includes(value as Language);
}
