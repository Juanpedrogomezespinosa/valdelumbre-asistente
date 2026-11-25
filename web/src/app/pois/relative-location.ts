import { Texts } from '../i18n/texts';
import { Coordinates, compassPoint, distanceInMetres, offsetInMetres } from './map-geometry';

export interface Landmark {
  name: string;
  coordinates: Coordinates;
}

/** Plaza Mayor: the point visitors orient themselves from in a Spanish village. */
export const LANDMARK_ID = 'poi-005';

const NEXT_TO_METRES = 50;

/** "A 120 m al oeste de Plaza Mayor": worked out from the coordinates, never invented. */
export function relativeLocation(point: Coordinates, landmark: Landmark, texts: Texts): string {
  const offset = offsetInMetres(landmark.coordinates, point);
  const metres = distanceInMetres(offset);
  const location = texts.location;
  if (metres < NEXT_TO_METRES) {
    return location.nextTo(landmark.name);
  }
  return location.away(
    formatDistance(metres, location.decimalSeparator),
    location.directions[compassPoint(offset)],
    landmark.name,
  );
}

export function formatDistance(metres: number, decimalSeparator: string): string {
  if (metres < 1000) {
    return `${Math.round(metres / 10) * 10} m`;
  }
  return `${(metres / 1000).toFixed(1).replace('.', decimalSeparator)} km`;
}
