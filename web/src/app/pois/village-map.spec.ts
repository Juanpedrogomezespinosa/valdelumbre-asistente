import { provideRouter } from '@angular/router';
import { render, screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { aPoi } from '../../testing/poi-fixture';
import { Poi } from './poi';
import { VillageMap } from './village-map';

const CASTLE = aPoi({
  id: 'poi-001',
  nombre: { texto: 'Castillo de Valdelumbre', idioma: 'es' },
  categoria: 'monumento',
  coordenadas: { lat: 40.4172, lon: -3.7051 },
});
const SQUARE = aPoi({
  id: 'poi-005',
  nombre: { texto: 'Plaza Mayor', idioma: 'es' },
  categoria: 'espacio_publico',
  coordenadas: { lat: 40.4168, lon: -3.7038 },
});
const WINERY = aPoi({
  id: 'poi-008',
  nombre: { texto: 'Bodega La Encina', idioma: 'es' },
  categoria: 'gastronomia',
  coordenadas: { lat: 40.405, lon: -3.73 },
});
const NOWHERE = aPoi({
  id: 'poi-099',
  nombre: { texto: 'Sin sitio', idioma: 'es' },
  coordenadas: null,
});

async function renderMap(inputs: { pois: Poi[]; highlighted?: string }) {
  localStorage.clear();
  return render(VillageMap, { inputs, providers: [provideRouter([])] });
}

function scaleInMetres(): number {
  return Number(/(\d+) m/.exec(scale())?.[1]);
}

function scale(): string {
  return screen.getByTestId('map-scale').textContent?.trim() ?? '';
}

describe('VillageMap', () => {
  it('is a labelled, focusable group with instructions and one button per located place', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, NOWHERE] });

    const map = screen.getByRole('group', { name: 'Mapa del pueblo' });
    expect(map).toHaveAttribute('tabindex', '0');
    expect(map).toHaveAccessibleDescription(/Arrastra para moverte/);
    expect(
      within(map)
        .getAllByRole('button', { name: /, / })
        .map((button) => button.getAttribute('aria-label')),
    ).toEqual(['Castillo de Valdelumbre, Monumento', 'Plaza Mayor, Espacio público']);
    expect(
      screen.getByText('1 punto no aparece en el mapa porque no tiene ubicación.'),
    ).toBeVisible();
  });

  it('shows the card of the place chosen on the map', async () => {
    await renderMap({ pois: [CASTLE, SQUARE] });
    expect(screen.getByText('Elige un punto del mapa para ver su ficha.')).toBeVisible();

    const marker = screen.getByRole('button', { name: 'Plaza Mayor, Espacio público' });
    await userEvent.click(marker);

    expect(marker).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('heading', { name: 'Plaza Mayor' })).toBeVisible();
    expect(screen.getByRole('link', { name: 'Plaza Mayor' })).toHaveAttribute(
      'href',
      '/pois/poi-005',
    );
  });

  it('zooms in and out with its buttons', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY] });
    const whole = scale();

    await userEvent.click(screen.getByRole('button', { name: 'Acercar' }));
    await userEvent.click(screen.getByRole('button', { name: 'Acercar' }));
    expect(scale()).not.toBe(whole);

    await userEvent.click(screen.getByRole('button', { name: 'Ver todo el pueblo' }));
    expect(scale()).toBe(whole);
  });

  it('zooms with the keyboard when the map has focus', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY] });
    const whole = scale();
    screen.getByRole('group', { name: 'Mapa del pueblo' }).focus();

    await userEvent.keyboard('++');
    expect(scale()).not.toBe(whole);

    await userEvent.keyboard('0');
    expect(scale()).toBe(whole);
  });

  it('marks the place the page is about and starts close to it when it is in the centre', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY], highlighted: 'poi-001' });

    expect(
      screen.getByRole('button', { name: 'Castillo de Valdelumbre, Monumento' }),
    ).toHaveAttribute('aria-current', 'location');
    expect(scaleInMetres()).toBeLessThanOrEqual(250);
  });

  it('starts with the whole village when the place is far from the centre', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY], highlighted: 'poi-008' });

    expect(scaleInMetres()).toBeGreaterThanOrEqual(500);
  });
});

describe('VillageMap focus', () => {
  it('never stays scrolled inside: the view moves instead of the stage', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY] });
    const stage = screen.getByRole('group', { name: 'Mapa del pueblo' });

    stage.scrollTop = 120;
    stage.scrollLeft = 80;
    stage.dispatchEvent(new Event('scroll'));

    expect(stage.scrollTop).toBe(0);
    expect(stage.scrollLeft).toBe(0);
  });
});
