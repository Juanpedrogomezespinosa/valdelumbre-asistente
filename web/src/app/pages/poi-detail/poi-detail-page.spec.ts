import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { screen, within } from '@testing-library/angular';
import { aPoi } from '../../../testing/poi-fixture';
import { providePageTitles } from '../../navigation/page-titles';
import { Poi } from '../../pois/poi';
import { PoiDetailPage } from './poi-detail-page';

async function openDetail(id = 'poi-003') {
  localStorage.clear();
  TestBed.configureTestingModule({
    providers: [
      provideRouter([{ path: 'pois/:id', component: PoiDetailPage, title: 'poiDetail' }]),
      provideHttpClient(),
      provideHttpClientTesting(),
      providePageTitles(),
    ],
  });
  const harness = await RouterTestingHarness.create(`/pois/${id}`);
  return { harness, http: TestBed.inject(HttpTestingController) };
}

/** The page also loads the whole catalogue for its map; these tests do not need it. */
function answerCatalogue(http: HttpTestingController, pois: Poi[] = []) {
  http.expectOne('/api/pois?idioma=es').flush(pois);
}

async function showDetail(poi: Poi) {
  const { harness, http } = await openDetail(poi.id);
  const request = http.expectOne(`/api/pois/${poi.id}?idioma=es`);
  request.flush(poi);
  answerCatalogue(http);
  await harness.fixture.whenStable();
}

function fact(term: string): string | null {
  const termElement = screen.getByText(term, { selector: 'dt' });
  return termElement.nextElementSibling?.textContent?.trim() ?? null;
}

describe('POI detail page', () => {
  it('shows the name, the description and every fact of the point', async () => {
    await showDetail(aPoi());

    expect(screen.getByRole('heading', { level: 1, name: 'Museo del Aceite' })).toBeVisible();
    expect(screen.getByText('Museo etnográfico sobre la almazara tradicional.')).toBeVisible();
    expect(fact('Categoría')).toBe('Museo');
    expect(fact('Accesibilidad')).toBe('Accesible');
    expect(fact('Ahora')).toBe('Cerrado');
    expect(fact('Precio')).toBe('Gratis');
  });

  it('titles the browser tab with the name of the point', async () => {
    await showDetail(aPoi());

    await vi.waitFor(() => expect(document.title).toBe('Museo del Aceite · Valdelumbre'));
  });

  it('writes the opening hours in words', async () => {
    await showDetail(aPoi());

    expect(screen.getByRole('heading', { level: 2, name: 'Horario' })).toBeVisible();
    expect(screen.getByText('Martes a domingo, de 10:00 a 18:00')).toBeVisible();
  });

  it('says unknown opening hours are unknown, not closed, and where to ask', async () => {
    await showDetail(
      aPoi({ id: 'poi-018', horario: { siempre_abierto: false, conocido: false, franjas: [] } }),
    );

    expect(
      screen.getByText('Horario no disponible: consulta en la Oficina de Turismo.'),
    ).toBeVisible();
  });

  it('says when a place is always open', async () => {
    await showDetail(
      aPoi({ id: 'poi-005', horario: { siempre_abierto: true, conocido: true, franjas: [] } }),
    );

    expect(screen.getByText('Abierto todos los días, a cualquier hora.')).toBeVisible();
  });

  it('marks an untranslated description with its language', async () => {
    await showDetail(aPoi({ descripcion: { texto: 'Solo en español.', idioma: 'en' } }));

    expect(screen.getByText('Solo en español.')).toHaveAttribute('lang', 'en');
  });

  it('tells a missing point apart from a loading error', async () => {
    const { harness, http } = await openDetail('poi-999');
    http
      .expectOne('/api/pois/poi-999?idioma=es')
      .flush({ detail: 'No existe' }, { status: 404, statusText: 'Not Found' });
    answerCatalogue(http);
    await harness.fixture.whenStable();

    expect(screen.getByRole('status')).toHaveTextContent('Este punto no existe en el catálogo.');
    expect(screen.getByRole('link', { name: 'Volver a los puntos de interés' })).toHaveAttribute(
      'href',
      '/pois',
    );
  });
});

describe('POI detail page location', () => {
  const SQUARE = aPoi({
    id: 'poi-005',
    nombre: { texto: 'Plaza Mayor', idioma: 'es' },
    categoria: 'espacio_publico',
    coordenadas: { lat: 40.4168, lon: -3.7038 },
  });
  const CASTLE = aPoi({
    id: 'poi-001',
    nombre: { texto: 'Castillo de Valdelumbre', idioma: 'es' },
    categoria: 'monumento',
    coordenadas: { lat: 40.4172, lon: -3.7051 },
  });

  async function showWithCatalogue(poi: Poi) {
    const { harness, http } = await openDetail(poi.id);
    http.expectOne(`/api/pois/${poi.id}?idioma=es`).flush(poi);
    answerCatalogue(http, [CASTLE, SQUARE]);
    await harness.fixture.whenStable();
  }

  it('says where the place is from the square and marks it on the map', async () => {
    await showWithCatalogue(CASTLE);

    const location = screen.getByRole('region', { name: 'Ubicación' });
    expect(within(location).getByText('A 120 m al oeste de Plaza Mayor')).toBeVisible();
    expect(
      within(location).getByRole('button', { name: 'Castillo de Valdelumbre, Monumento' }),
    ).toHaveAttribute('aria-current', 'location');
  });

  it('lists the nearest places with their distance, as links', async () => {
    await showWithCatalogue(CASTLE);

    const nearby = screen.getByRole('list', { name: 'Cerca de aquí, en línea recta' });
    const item = within(nearby).getByRole('listitem');
    expect(item).toHaveTextContent('Plaza Mayor');
    expect(item).toHaveTextContent('120 m');
    expect(within(item).getByRole('link', { name: 'Plaza Mayor' })).toHaveAttribute(
      'href',
      '/pois/poi-005',
    );
  });

  it('says so when the catalogue has no location for the place', async () => {
    await showWithCatalogue(aPoi({ id: 'poi-001', coordenadas: null }));

    expect(screen.getByText('El catálogo no tiene la ubicación de este punto.')).toBeVisible();
  });
});
