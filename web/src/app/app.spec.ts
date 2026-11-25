import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { App } from './app';
import { routes } from './app.routes';
import { providePageTitles } from './navigation/page-titles';

async function renderApp() {
  localStorage.clear();
  // Like the real app: title strategy registered and an initial navigation already done.
  return render(App, { routes, providers: [providePageTitles()], initialRoute: '/' });
}

describe('App shell', () => {
  it('offers a skip link to the main content', async () => {
    await renderApp();

    const skipLink = screen.getByRole('link', { name: 'Saltar al contenido' });
    expect(skipLink).toHaveAttribute('href', '#main');
    expect(screen.getByRole('main')).toHaveAttribute('id', 'main');
  });

  it('has a labelled main navigation with the assistant and the points of interest', async () => {
    await renderApp();

    const navigation = screen.getByRole('navigation', { name: 'Principal' });
    expect(navigation).toContainElement(screen.getByRole('link', { name: 'Asistente' }));
    expect(navigation).toContainElement(screen.getByRole('link', { name: 'Puntos de interés' }));
  });

  it('switches the interface language from a labelled selector', async () => {
    await renderApp();

    await userEvent.selectOptions(screen.getByLabelText('Idioma'), 'en');

    expect(await screen.findByRole('link', { name: 'Assistant' })).toBeInTheDocument();
    expect(document.documentElement.lang).toBe('en');
  });

  it('shows the remembered language as selected when the app starts', async () => {
    localStorage.setItem('valdelumbre.idioma', 'en');
    await render(App, { routes, providers: [providePageTitles()], initialRoute: '/' });

    expect(screen.getByLabelText('Language')).toHaveValue('en');
  });

  it('moves focus to the page heading and updates the title after navigating', async () => {
    const { navigate } = await renderApp();

    await navigate('/pois');

    const heading = await screen.findByRole('heading', { level: 1, name: 'Puntos de interés' });
    await vi.waitFor(() => expect(heading).toHaveFocus());
    expect(document.title).toBe('Puntos de interés · Valdelumbre');
  });

  it('titles the page in the current language', async () => {
    const { navigate } = await renderApp();
    await navigate('/pois');

    await userEvent.selectOptions(screen.getByLabelText('Idioma'), 'en');

    await vi.waitFor(() => expect(document.title).toBe('Points of interest · Valdelumbre'));
  });

  it('shows a not found page for unknown addresses', async () => {
    const { navigate } = await renderApp();

    await navigate('/no-existe');

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Página no encontrada' }),
    ).toBeInTheDocument();
  });
});
