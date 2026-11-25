import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { aPoi } from '../../../testing/poi-fixture';
import { CLOCK } from '../../clock';
import { PoiListPage } from './poi-list-page';

const A_WEDNESDAY_MORNING = new Date('2026-11-25T09:20:00Z');

async function openList(url = '/pois') {
  localStorage.clear();
  TestBed.configureTestingModule({
    providers: [
      provideRouter([{ path: 'pois', component: PoiListPage }]),
      provideHttpClient(),
      provideHttpClientTesting(),
      { provide: CLOCK, useValue: () => A_WEDNESDAY_MORNING },
    ],
  });
  const harness = await RouterTestingHarness.create(url);
  return { harness, http: TestBed.inject(HttpTestingController) };
}

function answer(http: HttpTestingController, count: number) {
  const request = http.expectOne((r) => r.url === '/api/pois');
  request.flush(Array.from({ length: count }, (_, i) => aPoi({ id: `poi-${i}` })));
  return request.request.params;
}

describe('POI list page', () => {
  it('lists the points of interest and announces how many there are', async () => {
    const { harness, http } = await openList();

    expect(screen.getByRole('status')).toHaveTextContent('Cargando puntos…');
    answer(http, 3);
    await harness.fixture.whenStable();

    expect(await screen.findByRole('status')).toHaveTextContent('3 puntos encontrados');
    expect(screen.getAllByRole('listitem')).toHaveLength(3);
  });

  it('applies the filters found in the URL and shows them in the form', async () => {
    const { http } = await openList('/pois?categoria=museo&accesible=false');

    const params = answer(http, 1);

    expect(params.get('categoria')).toBe('museo');
    expect(params.get('accesible')).toBe('false');
    expect(params.get('idioma')).toBe('es');
    expect(screen.getByLabelText('Categoría')).toHaveValue('museo');
    expect(screen.getByLabelText('Accesibilidad')).toHaveValue('false');
  });

  it('writes a changed filter into the URL and asks the API again', async () => {
    const { http } = await openList();
    answer(http, 2);

    await userEvent.selectOptions(screen.getByLabelText('Categoría'), 'museo');

    await vi.waitFor(() => expect(TestBed.inject(Router).url).toBe('/pois?categoria=museo'));
    expect(answer(http, 1).get('categoria')).toBe('museo');
  });

  it('asks for what is open at this very moment when "open now" is ticked', async () => {
    const { http } = await openList();
    answer(http, 2);

    await userEvent.click(screen.getByLabelText('Abierto ahora'));

    await vi.waitFor(() => expect(TestBed.inject(Router).url).toBe('/pois?abierto=ahora'));
    expect(answer(http, 1).get('abierto_en')).toBe('2026-11-25T09:20:00.000Z');
  });

  it('says so when no point matches', async () => {
    const { harness, http } = await openList('/pois?categoria=ruta');
    answer(http, 0);
    await harness.fixture.whenStable();

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Ningún punto cumple estos filtros',
    );
  });

  it('explains when the points cannot be loaded', async () => {
    const { harness, http } = await openList();
    http
      .expectOne((r) => r.url === '/api/pois')
      .flush('caída', {
        status: 503,
        statusText: 'Service Unavailable',
      });
    await harness.fixture.whenStable();

    expect(await screen.findByRole('status')).toHaveTextContent(
      'No se han podido cargar los puntos',
    );
  });
});

describe('POI list page views', () => {
  it('switches between list and map, keeping the view in the URL', async () => {
    const { harness, http } = await openList();
    answer(http, 2);
    await harness.fixture.whenStable();

    const views = screen.getByRole('group', { name: 'Vista' });
    expect(within(views).getByRole('button', { name: 'Lista' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );

    await userEvent.click(within(views).getByRole('button', { name: 'Mapa' }));

    await vi.waitFor(() => expect(TestBed.inject(Router).url).toBe('/pois?vista=mapa'));
    answer(http, 2);
    await harness.fixture.whenStable();
    expect(screen.getByRole('group', { name: 'Mapa del pueblo' })).toBeInTheDocument();
    expect(screen.queryByRole('list')).toBeNull();
  });

  it('keeps the map view when a filter changes', async () => {
    const { http } = await openList('/pois?vista=mapa');
    answer(http, 2);

    await userEvent.selectOptions(screen.getByLabelText('Categoría'), 'museo');

    await vi.waitFor(() =>
      expect(TestBed.inject(Router).url).toBe('/pois?vista=mapa&categoria=museo'),
    );
  });
});
