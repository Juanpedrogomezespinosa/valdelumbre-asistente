import { Language } from '../i18n/language';

// Field names follow the API contract (D-021), so they stay in Spanish.

export type Category =
  'monumento' | 'museo' | 'naturaleza' | 'ruta' | 'gastronomia' | 'servicio' | 'espacio_publico';

export const CATEGORIES: readonly Category[] = [
  'monumento',
  'museo',
  'naturaleza',
  'ruta',
  'gastronomia',
  'servicio',
  'espacio_publico',
];

export interface ServedText {
  texto: string;
  idioma: Language;
}

export interface Season {
  desde: string;
  hasta: string;
}

export interface Slot {
  dias: number[];
  abre: string;
  cierra: string;
  temporada: Season | null;
}

export interface Schedule {
  siempre_abierto: boolean;
  conocido: boolean;
  franjas: Slot[];
}

export interface Price {
  minimo: number | null;
  maximo: number | null;
  texto: string;
}

export interface Poi {
  id: string;
  nombre: ServedText;
  descripcion: ServedText;
  categoria: Category;
  coordenadas: { lat: number; lon: number } | null;
  accesible: boolean | null;
  abierto_ahora: boolean | null;
  horario: Schedule;
  precio: Price;
  etiquetas: string[];
}

export function isCategory(value: unknown): value is Category {
  return CATEGORIES.includes(value as Category);
}
