import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';
import { screen, within } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { aPoi } from '../../../testing/poi-fixture';
import { I18n } from '../../i18n/i18n';
import { AssistantPage } from './assistant-page';

async function openAssistant() {
  localStorage.clear();
  TestBed.configureTestingModule({
    providers: [
      provideRouter([{ path: '', component: AssistantPage }]),
      provideHttpClient(),
      provideHttpClientTesting(),
    ],
  });
  const harness = await RouterTestingHarness.create('/');
  return { harness, http: TestBed.inject(HttpTestingController) };
}

/** Card requests only start once the answer has been processed, so wait for them to appear. */
function pending(http: HttpTestingController, url: string) {
  return vi.waitFor(() => http.expectOne(url));
}

async function ask(question: string) {
  await userEvent.type(screen.getByLabelText('Tu pregunta'), question);
  await userEvent.click(screen.getByRole('button', { name: 'Preguntar' }));
}

describe('Assistant page', () => {
  it('has a labelled question box with examples and a submit button', async () => {
    await openAssistant();

    const box = screen.getByLabelText('Tu pregunta');
    expect(box).toHaveAccessibleDescription(/Por ejemplo/);
    expect(screen.getByRole('button', { name: 'Preguntar' })).toBeVisible();
  });

  it('sends the question in the interface language and announces the answer', async () => {
    const { harness, http } = await openAssistant();
    await ask('¿Qué museos son accesibles?');

    const request = http.expectOne('/api/preguntar');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ pregunta: '¿Qué museos son accesibles?', idioma: 'es' });
    expect(screen.getByRole('status')).toHaveTextContent('Buscando en el catálogo…');

    request.flush({
      respuesta: 'He encontrado 1 lugar en el catálogo:\n- Museo del Aceite (museo · accesible)',
      ids: ['poi-003'],
    });
    (await pending(http, '/api/pois/poi-003?idioma=es')).flush(aPoi());
    await harness.fixture.whenStable();

    const answer = screen.getByRole('status');
    expect(answer).toHaveTextContent('He encontrado 1 lugar en el catálogo:');
    expect(within(answer).getByRole('listitem')).toHaveTextContent(
      'Museo del Aceite (museo · accesible)',
    );
  });

  it('shows the card of every cited point, outside the announced answer', async () => {
    const { harness, http } = await openAssistant();
    await ask('museos accesibles');
    http.expectOne('/api/preguntar').flush({ respuesta: '…', ids: ['poi-003', 'poi-015'] });
    (await pending(http, '/api/pois/poi-003?idioma=es')).flush(aPoi());
    (await pending(http, '/api/pois/poi-015?idioma=es')).flush(
      aPoi({ id: 'poi-015', nombre: { texto: 'Centro del Valle', idioma: 'es' } }),
    );
    await harness.fixture.whenStable();

    const cited = screen.getByRole('region', { name: 'Puntos en los que se apoya la respuesta' });
    expect(within(cited).getByRole('link', { name: 'Museo del Aceite' })).toBeVisible();
    expect(within(cited).getByRole('link', { name: 'Centro del Valle' })).toBeVisible();
    expect(screen.getByRole('status')).not.toContainElement(cited);
  });

  it('shows no cards when the answer cites nothing', async () => {
    const { harness, http } = await openAssistant();
    await ask('¿Hay tirolina?');
    http.expectOne('/api/preguntar').flush({
      respuesta: 'No tengo información sobre eso en el catálogo de Valdelumbre.',
      ids: [],
    });
    await harness.fixture.whenStable();

    expect(screen.getByRole('status')).toHaveTextContent('No tengo información');
    expect(screen.queryByRole('region')).toBeNull();
  });

  it('shows the message the API sends for an invalid question', async () => {
    const { harness, http } = await openAssistant();
    await ask('x');
    http
      .expectOne('/api/preguntar')
      .flush(
        { detail: 'La pregunta no puede estar vacía ni superar los 500 caracteres.' },
        { status: 422, statusText: 'Unprocessable Entity' },
      );
    await harness.fixture.whenStable();

    expect(screen.getByRole('status')).toHaveTextContent(
      'La pregunta no puede estar vacía ni superar los 500 caracteres.',
    );
    const box = screen.getByLabelText('Tu pregunta');
    expect(box).toBeInvalid();
    expect(box).toHaveAccessibleDescription(/no puede estar vacía/);
  });

  it('does not mark the question as invalid when the assistant cannot be reached', async () => {
    const { harness, http } = await openAssistant();
    await ask('hola');
    http.expectOne('/api/preguntar').error(new ProgressEvent('error'));
    await harness.fixture.whenStable();

    expect(screen.getByLabelText('Tu pregunta')).toBeValid();
  });

  it('explains when the assistant cannot be reached', async () => {
    const { harness, http } = await openAssistant();
    await ask('hola');
    http.expectOne('/api/preguntar').error(new ProgressEvent('error'));
    await harness.fixture.whenStable();

    expect(screen.getByRole('status')).toHaveTextContent(
      'No se ha podido contactar con el asistente',
    );
  });

  it('asks in English when the interface is in English', async () => {
    const { harness, http } = await openAssistant();
    TestBed.inject(I18n).use('en');
    await harness.fixture.whenStable();

    await userEvent.type(screen.getByLabelText('Your question'), 'Kids outdoors?');
    await userEvent.click(screen.getByRole('button', { name: 'Ask' }));

    expect(http.expectOne('/api/preguntar').request.body).toEqual({
      pregunta: 'Kids outdoors?',
      idioma: 'en',
    });
  });
});

describe('Assistant page headings', () => {
  it('nests the cited cards under the section heading', async () => {
    const { harness, http } = await openAssistant();
    await ask('museos');
    http.expectOne('/api/preguntar').flush({ respuesta: '…', ids: ['poi-003'] });
    (await pending(http, '/api/pois/poi-003?idioma=es')).flush(aPoi());
    await harness.fixture.whenStable();

    expect(screen.getByRole('heading', { level: 3, name: 'Museo del Aceite' })).toBeVisible();
  });
});
