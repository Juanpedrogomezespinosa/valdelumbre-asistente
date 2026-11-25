import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { screen } from '@testing-library/angular';
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

async function showDetail(poi: Poi) {
  const { harness, http } = await openDetail(poi.id);
  const request = http.expectOne(`/api/pois/${poi.id}?idioma=es`);
  request.flush(poi);
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
    await harness.fixture.whenStable();

    expect(screen.getByRole('status')).toHaveTextContent('Este punto no existe en el catálogo.');
    expect(screen.getByRole('link', { name: 'Volver a los puntos de interés' })).toHaveAttribute(
      'href',
      '/pois',
    );
  });
});
