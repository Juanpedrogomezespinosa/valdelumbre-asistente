import { TEXTS } from '../i18n/texts';
import { daysText, seasonText, slotText } from './schedule-text';

const es = TEXTS.es;
const en = TEXTS.en;

describe('Opening hours in words', () => {
  it.each([
    [[1, 2, 3, 4, 5, 6, 7], 'todos los días', 'every day'],
    [[2, 3, 4, 5, 6, 7], 'martes a domingo', 'Tuesday to Sunday'],
    [[5, 6], 'viernes y sábado', 'Friday and Saturday'],
    [[6], 'sábado', 'Saturday'],
    [[1, 3, 5], 'lunes, miércoles y viernes', 'Monday, Wednesday and Friday'],
    [[1, 2, 3, 6], 'lunes a miércoles y sábado', 'Monday to Wednesday and Saturday'],
  ])('reads ISO days %j as "%s" / "%s"', (days, spanish, english) => {
    expect(daysText(days, es)).toBe(spanish);
    expect(daysText(days, en)).toBe(english);
  });

  it('reads a season in each language', () => {
    const summer = { desde: '06-01', hasta: '09-30' };

    expect(seasonText(summer, es)).toBe('del 1 de junio al 30 de septiembre');
    expect(seasonText(summer, en)).toBe('from 1 June to 30 September');
  });

  it('writes a whole slot as one sentence', () => {
    const slot = { dias: [2, 3, 4, 5, 6, 7], abre: '10:00', cierra: '18:00', temporada: null };

    expect(slotText(slot, es)).toBe('Martes a domingo, de 10:00 a 18:00');
    expect(slotText(slot, en)).toBe('Tuesday to Sunday, from 10:00 to 18:00');
  });

  it('adds the season to a seasonal slot', () => {
    const slot = {
      dias: [1, 2, 3, 4, 5, 6, 7],
      abre: '11:00',
      cierra: '20:00',
      temporada: { desde: '06-01', hasta: '09-30' },
    };

    expect(slotText(slot, es)).toBe(
      'Todos los días, de 11:00 a 20:00 (del 1 de junio al 30 de septiembre)',
    );
  });
});
