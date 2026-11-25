import { TEXTS } from '../i18n/texts';
import { relativeLocation } from './relative-location';

const PLAZA = { name: 'Plaza Mayor', coordinates: { lat: 40.4168, lon: -3.7038 } };

describe('relativeLocation', () => {
  it('gives distance and direction from the reference place', () => {
    // Castillo de Valdelumbre: about 115 m west-northwest of the square.
    const text = relativeLocation({ lat: 40.4172, lon: -3.7051 }, PLAZA, TEXTS.es);

    expect(text).toBe('A 120 m al oeste de Plaza Mayor');
  });

  it('switches to kilometres with a decimal comma in Spanish', () => {
    // Bodega La Encina, far to the south-west.
    expect(relativeLocation({ lat: 40.405, lon: -3.73 }, PLAZA, TEXTS.es)).toBe(
      'A 2,6 km al suroeste de Plaza Mayor',
    );
  });

  it('writes the English form', () => {
    expect(relativeLocation({ lat: 40.405, lon: -3.73 }, PLAZA, TEXTS.en)).toBe(
      '2.6 km southwest of Plaza Mayor',
    );
  });

  it('says "next to" when the place is very close', () => {
    expect(relativeLocation({ lat: 40.4169, lon: -3.7039 }, PLAZA, TEXTS.es)).toBe(
      'Junto a Plaza Mayor',
    );
  });
});
