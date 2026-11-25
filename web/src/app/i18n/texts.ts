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
  notFound: {
    message: 'This address does not match any page.',
    backHome: 'Back to the assistant',
  },
};

export const TEXTS: Record<Language, Texts> = { es, en };

export type PageKey = keyof Texts['pages'];
