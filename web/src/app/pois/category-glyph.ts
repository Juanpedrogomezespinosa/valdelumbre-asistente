import { Category } from './poi';

/** 24×24 icon paths for the map markers. Decorative: the category is also in the name. */
export const CATEGORY_GLYPHS: Record<Category, string> = {
  monumento: 'M4 20V8h2.5v2.5h2.5V8h2.5v2.5h2.5V8h2.5v2.5h2.5V8H20v12h-5.5v-4a2.5 2.5 0 0 0-5 0v4z',
  museo:
    'M12 3 21 8H3zM4 9.5h16V11H4zM5.5 12.5h2.5v5H5.5zm5.25 0h2.5v5h-2.5zm5.25 0h2.5v5H16zM3 19h18v2H3z',
  naturaleza: 'M12 2 18.5 11H15l4.5 7h-6v4h-3v-4h-6L9 11H5.5z',
  ruta: 'M6 2h2v20H6zM8 3h10l-2.5 3.5L18 10H8z',
  gastronomia: 'M7 2h10c0 6.5-2.4 9-5 9s-5-2.5-5-9zM11 11h2v8h4v2H7v-2h4z',
  servicio: 'M10.5 4h3v3h-3zM9 9h4.5v9H15v2H9v-2h1.5v-7H9z',
  espacio_publico: 'M2 20V7h20v13h-3.5v-5.5a2.5 2.5 0 0 0-5 0V20h-3v-5.5a2.5 2.5 0 0 0-5 0V20z',
};
