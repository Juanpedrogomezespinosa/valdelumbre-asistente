import { Texts } from '../i18n/texts';

/** Accessibility in words, with "no data" as a state of its own (D-008). */
export function accessibilityText(accessible: boolean | null, texts: Texts): string {
  if (accessible === null) {
    return texts.poi.accessibilityUnknown;
  }
  return accessible ? texts.poi.accessible : texts.poi.notAccessible;
}

/** "Open now" in words; unknown hours are not "closed" (D-009). */
export function openNowText(open: boolean | null, texts: Texts): string {
  if (open === null) {
    return texts.poi.hoursUnknown;
  }
  return open ? texts.poi.open : texts.poi.closed;
}
