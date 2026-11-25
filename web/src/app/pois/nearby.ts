import { Texts } from '../i18n/texts';
import { distanceInMetres, offsetInMetres } from './map-geometry';
import { Poi } from './poi';
import { formatDistance } from './relative-location';

export interface NearbyPlace {
  poi: Poi;
  distance: string;
}

/** The `count` closest places, as the crow flies, worked out from the coordinates. */
export function nearby(
  place: Poi,
  catalogue: readonly Poi[],
  count: number,
  texts: Texts,
): NearbyPlace[] {
  const origin = place.coordenadas;
  if (!origin) {
    return [];
  }
  return catalogue
    .filter((poi) => poi.id !== place.id && poi.coordenadas !== null)
    .map((poi) => ({
      poi,
      metres: distanceInMetres(offsetInMetres(origin, poi.coordenadas ?? origin)),
    }))
    .sort((a, b) => a.metres - b.metres)
    .slice(0, count)
    .map(({ poi, metres }) => ({
      poi,
      distance: formatDistance(metres, texts.location.decimalSeparator),
    }));
}
