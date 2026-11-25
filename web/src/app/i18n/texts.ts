import { Language } from './language';

const es = {
  siteName: 'Valdelumbre',
  skipToContent: 'Saltar al contenido',
  nav: { label: 'Principal', assistant: 'Asistente', pois: 'Puntos de interés' },
  languageLabel: 'Idioma',
  pages: {
    assistant: 'Pregunta al asistente',
    pois: 'Puntos de interés',
    poiDetail: 'Ficha del punto',
    notFound: 'Página no encontrada',
  },
  categories: {
    monumento: 'Monumento',
    museo: 'Museo',
    naturaleza: 'Naturaleza',
    ruta: 'Ruta',
    gastronomia: 'Gastronomía',
    servicio: 'Servicio',
    espacio_publico: 'Espacio público',
  },
  poi: {
    category: 'Categoría',
    accessibility: 'Accesibilidad',
    openNow: 'Ahora',
    price: 'Precio',
    accessible: 'Accesible',
    notAccessible: 'No accesible',
    accessibilityUnknown: 'Sin datos de accesibilidad',
    open: 'Abierto',
    closed: 'Cerrado',
    hoursUnknown: 'Horario no disponible',
  },
  poiList: {
    filters: 'Filtros',
    anyCategory: 'Todas',
    anyAccessibility: 'Cualquiera',
    onlyAccessible: 'Solo accesibles',
    onlyNotAccessible: 'Solo no accesibles',
    openNow: 'Abierto ahora',
    loading: 'Cargando puntos…',
    loadError: 'No se han podido cargar los puntos. Inténtalo de nuevo en unos minutos.',
    none: 'Ningún punto cumple estos filtros.',
    found: (count: number) => (count === 1 ? '1 punto encontrado' : `${count} puntos encontrados`),
  },
  notFound: {
    message: 'La dirección no corresponde a ninguna página.',
    backHome: 'Volver al asistente',
  },
};

export type Texts = typeof es;

const en: Texts = {
  siteName: 'Valdelumbre',
  skipToContent: 'Skip to content',
  nav: { label: 'Main', assistant: 'Assistant', pois: 'Points of interest' },
  languageLabel: 'Language',
  pages: {
    assistant: 'Ask the assistant',
    pois: 'Points of interest',
    poiDetail: 'Point of interest',
    notFound: 'Page not found',
  },
  categories: {
    monumento: 'Monument',
    museo: 'Museum',
    naturaleza: 'Nature',
    ruta: 'Route',
    gastronomia: 'Food and drink',
    servicio: 'Service',
    espacio_publico: 'Public space',
  },
  poi: {
    category: 'Category',
    accessibility: 'Accessibility',
    openNow: 'Now',
    price: 'Price',
    accessible: 'Accessible',
    notAccessible: 'Not accessible',
    accessibilityUnknown: 'No accessibility data',
    open: 'Open',
    closed: 'Closed',
    hoursUnknown: 'Opening hours not available',
  },
  poiList: {
    filters: 'Filters',
    anyCategory: 'All',
    anyAccessibility: 'Any',
    onlyAccessible: 'Accessible only',
    onlyNotAccessible: 'Not accessible only',
    openNow: 'Open now',
    loading: 'Loading points…',
    loadError: 'The points could not be loaded. Please try again in a few minutes.',
    none: 'No point matches these filters.',
    found: (count: number) => (count === 1 ? '1 point found' : `${count} points found`),
  },
  notFound: {
    message: 'This address does not match any page.',
    backHome: 'Back to the assistant',
  },
};

export const TEXTS: Record<Language, Texts> = { es, en };

export type PageKey = keyof Texts['pages'];
