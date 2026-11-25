export interface AnswerParts {
  paragraphs: string[];
  items: string[];
}

const ITEM_MARK = '- ';

/**
 * The API answers in plain text, one "- " line per place. Shown as a real list, a screen
 * reader announces the number of places instead of reading out each dash.
 */
export function splitAnswer(text: string): AnswerParts {
  const lines = text.split('\n').filter((line) => line.trim() !== '');
  return {
    paragraphs: lines.filter((line) => !line.startsWith(ITEM_MARK)),
    items: lines
      .filter((line) => line.startsWith(ITEM_MARK))
      .map((line) => line.slice(ITEM_MARK.length)),
  };
}
