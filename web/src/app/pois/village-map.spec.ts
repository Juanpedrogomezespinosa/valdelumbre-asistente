import { provideRouter } from '@angular/router';
import { render, screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { aPoi } from '../../testing/poi-fixture';
import { Poi } from './poi';
import { VillageMap } from './village-map';

const CASTLE = aPoi({
  id: 'poi-001',
  nombre: { texto: 'Castillo de Valdelumbre', idioma: 'es' },
  coordenadas: { lat: 40.4172, lon: -3.7051 },
});
const SQUARE = aPoi({
  id: 'poi-005',
  nombre: { texto: 'Plaza Mayor', idioma: 'es' },
  coordenadas: { lat: 40.4168, lon: -3.7038 },
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

describe('VillageMap', () => {
  it('is a labelled group with one link per located place', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, NOWHERE] });

    const map = screen.getByRole('group', { name: 'Mapa del pueblo' });
    const links = within(map).getAllByRole('link');
    expect(links.map((link) => link.getAttribute('aria-label'))).toEqual([
      'Castillo de Valdelumbre',
      'Plaza Mayor',
    ]);
    expect(links[0]).toHaveAttribute('href', '/pois/poi-001');
  });

  it('says in words how many places could not be drawn', async () => {
    await renderMap({ pois: [CASTLE, NOWHERE] });

    expect(
      screen.getByText('1 punto no aparece en el mapa porque no tiene ubicación.'),
    ).toBeVisible();
  });

  it('marks the highlighted place as the current one', async () => {
    await renderMap({ pois: [CASTLE, SQUARE], highlighted: 'poi-001' });

    expect(screen.getByRole('link', { name: 'Castillo de Valdelumbre' })).toHaveAttribute(
      'aria-current',
      'location',
    );
    expect(screen.getByRole('link', { name: 'Plaza Mayor' })).not.toHaveAttribute('aria-current');
  });
});

describe('VillageMap zoom on the village centre', () => {
  const WINERY = aPoi({
    id: 'poi-008',
    nombre: { texto: 'Bodega La Encina', idioma: 'es' },
    coordenadas: { lat: 40.405, lon: -3.73 },
  });

  it('can zoom on the centre, leaving far places out and saying how many', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY] });
    const zoom = screen.getByRole('button', { name: 'Ver el centro del pueblo' });
    expect(zoom).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByRole('link', { name: 'Bodega La Encina' })).toBeInTheDocument();

    await userEvent.click(zoom);

    expect(zoom).toHaveAttribute('aria-pressed', 'true');
    expect(screen.queryByRole('link', { name: 'Bodega La Encina' })).toBeNull();
    expect(screen.getByRole('link', { name: 'Castillo de Valdelumbre' })).toBeInTheDocument();
    expect(screen.getByText('1 punto queda fuera de esta vista.')).toBeVisible();
  });

  it('starts zoomed in when the highlighted place is in the centre', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY], highlighted: 'poi-001' });

    expect(screen.getByRole('button', { name: 'Ver el centro del pueblo' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
  });

  it('starts with the whole village when the highlighted place is far away', async () => {
    await renderMap({ pois: [CASTLE, SQUARE, WINERY], highlighted: 'poi-008' });

    expect(screen.getByRole('button', { name: 'Ver el centro del pueblo' })).toHaveAttribute(
      'aria-pressed',
      'false',
    );
  });

  it('offers no zoom when the square is not among the places shown', async () => {
    await renderMap({ pois: [CASTLE, WINERY] });

    expect(screen.queryByRole('button', { name: 'Ver el centro del pueblo' })).toBeNull();
  });
});
