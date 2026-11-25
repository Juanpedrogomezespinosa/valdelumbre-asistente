import { TEXTS } from '../i18n/texts';
import { aPoi } from '../../testing/poi-fixture';
import { nearby } from './nearby';

const at = (id: string, lat: number, lon: number) =>
  aPoi({ id, nombre: { texto: id, idioma: 'es' }, coordenadas: { lat, lon } });

describe('nearby', () => {
  const castle = at('castillo', 40.4172, -3.7051);
  const church = at('iglesia', 40.4175, -3.7045);
  const square = at('plaza', 40.4168, -3.7038);
  const winery = at('bodega', 40.405, -3.73);
  const nowhere = aPoi({ id: 'sin-sitio', coordenadas: null });

  it('lists the closest places first, without the place itself', () => {
    const result = nearby(castle, [winery, square, castle, church, nowhere], 2, TEXTS.es);

    expect(result.map((entry) => entry.poi.id)).toEqual(['iglesia', 'plaza']);
    expect(result.map((entry) => entry.distance)).toEqual(['60 m', '120 m']);
  });

  it('has nothing to say for a place without coordinates', () => {
    expect(nearby(nowhere, [castle, church], 3, TEXTS.es)).toEqual([]);
  });
});
