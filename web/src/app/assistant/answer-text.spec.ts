import { splitAnswer } from './answer-text';

describe('splitAnswer', () => {
  it('separates the introduction from the listed places', () => {
    const text =
      'He encontrado 2 lugares en el catálogo:\n- Museo del Aceite (museo · accesible)\n- Centro (museo · accesible)';

    expect(splitAnswer(text)).toEqual({
      paragraphs: ['He encontrado 2 lugares en el catálogo:'],
      items: ['Museo del Aceite (museo · accesible)', 'Centro (museo · accesible)'],
    });
  });

  it('keeps an answer without a list as a paragraph', () => {
    expect(splitAnswer('No tengo información sobre eso en el catálogo de Valdelumbre.')).toEqual({
      paragraphs: ['No tengo información sobre eso en el catálogo de Valdelumbre.'],
      items: [],
    });
  });
});
