import { render, screen } from '@testing-library/angular';
import userEvent from '@testing-library/user-event';
import { ThemeToggle } from './theme-toggle';

const STORAGE_KEY = 'valdelumbre.tema';

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear();
    delete document.documentElement.dataset['theme'];
  });

  it('is a labelled toggle button that starts from the system theme', async () => {
    await render(ThemeToggle);

    const toggle = screen.getByRole('button', { name: 'Modo oscuro' });
    expect(toggle).toHaveAttribute('aria-pressed', 'false');
    expect(document.documentElement.dataset['theme']).toBeUndefined();
  });

  it('switches the page theme and remembers the choice', async () => {
    await render(ThemeToggle);
    const toggle = screen.getByRole('button', { name: 'Modo oscuro' });

    await userEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-pressed', 'true');
    expect(document.documentElement.dataset['theme']).toBe('dark');
    expect(localStorage.getItem(STORAGE_KEY)).toBe('dark');

    await userEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-pressed', 'false');
    expect(document.documentElement.dataset['theme']).toBe('light');
  });

  it('starts from the remembered choice', async () => {
    localStorage.setItem(STORAGE_KEY, 'dark');
    await render(ThemeToggle);

    expect(screen.getByRole('button', { name: 'Modo oscuro' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    expect(document.documentElement.dataset['theme']).toBe('dark');
  });
});
