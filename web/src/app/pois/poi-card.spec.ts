import { render, screen, within } from '@testing-library/angular';
import { provideRouter } from '@angular/router';
import { aPoi } from '../../testing/poi-fixture';
import { I18n } from '../i18n/i18n';
import { Poi } from './poi';
import { PoiCard } from './poi-card';

async function renderCard(poi: Poi) {
  localStorage.clear();
  return render(PoiCard, { inputs: { poi }, providers: [provideRouter([])] });
}

function fact(term: string): string | null {
  const termElement = screen.getByText(term, { selector: 'dt' });
  return termElement.nextElementSibling?.textContent?.trim() ?? null;
}

describe('PoiCard', () => {
  it('links the name to the detail page', async () => {
    await renderCard(aPoi());

    const heading = screen.getByRole('heading', { name: 'Museo del Aceite' });
    expect(within(heading).getByRole('link')).toHaveAttribute('href', '/pois/poi-003');
  });

  it('shows category, accessibility, opening and price as text', async () => {
    await renderCard(aPoi());

    expect(fact('Categoría')).toBe('Museo');
    expect(fact('Accesibilidad')).toBe('Accesible');
    expect(fact('Ahora')).toBe('Cerrado');
    expect(fact('Precio')).toBe('Gratis');
  });

  it('says in words when accessibility or opening hours are unknown', async () => {
    await renderCard(aPoi({ accesible: null, abierto_ahora: null }));

    expect(fact('Accesibilidad')).toBe('Sin datos de accesibilidad');
    expect(fact('Ahora')).toBe('Horario no disponible');
  });

  it('marks a name served in another language with its lang', async () => {
    const { fixture } = await renderCard(
      aPoi({ nombre: { texto: 'Ermita del Cerro', idioma: 'es' } }),
    );
    fixture.debugElement.injector.get(I18n).use('en');
    fixture.detectChanges();

    expect(await screen.findByText('Ermita del Cerro')).toHaveAttribute('lang', 'es');
    expect(fact('Accessibility')).toBe('Accessible');
  });
});
