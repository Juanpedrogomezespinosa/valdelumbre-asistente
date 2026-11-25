import { Poi } from '../app/pois/poi';

export function aPoi(overrides: Partial<Poi> = {}): Poi {
  return {
    id: 'poi-003',
    nombre: { texto: 'Museo del Aceite', idioma: 'es' },
    descripcion: { texto: 'Museo etnográfico sobre la almazara tradicional.', idioma: 'es' },
    categoria: 'museo',
    coordenadas: { lat: 40.4183, lon: -3.7012 },
    accesible: true,
    abierto_ahora: false,
    horario: {
      siempre_abierto: false,
      conocido: true,
      franjas: [{ dias: [2, 3, 4, 5, 6, 7], abre: '10:00', cierra: '18:00', temporada: null }],
    },
    precio: { minimo: 0, maximo: 0, texto: 'Gratis' },
    etiquetas: ['historia'],
    ...overrides,
  };
}
