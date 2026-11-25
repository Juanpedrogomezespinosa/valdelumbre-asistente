export interface Coordinates {
  lat: number;
  lon: number;
}

export interface Offset {
  east: number;
  north: number;
}

export interface Frame {
  centre: Coordinates;
  /** Half the extent of the frame, in metres from the centre. */
  halfWidth: number;
  halfHeight: number;
}

export interface Canvas {
  width: number;
  height: number;
  padding: number;
}

const METRES_PER_DEGREE_LAT = 111_320;

/**
 * Flat (equirectangular) approximation: at the scale of a village, a few kilometres, its
 * error is far below what a drawing can show (D-019).
 */
export function offsetInMetres(origin: Coordinates, point: Coordinates): Offset {
  const metresPerDegreeLon = METRES_PER_DEGREE_LAT * Math.cos((origin.lat * Math.PI) / 180);
  return {
    east: (point.lon - origin.lon) * metresPerDegreeLon,
    north: (point.lat - origin.lat) * METRES_PER_DEGREE_LAT,
  };
}

export function distanceInMetres(offset: Offset): number {
  return Math.hypot(offset.east, offset.north);
}

/** 0 = north, 1 = north-east … 7 = north-west. */
export function compassPoint(offset: Offset): number {
  const degrees = (Math.atan2(offset.east, offset.north) * 180) / Math.PI;
  return Math.round((degrees + 360) / 45) % 8;
}

/** `minimumHalfExtent` keeps one or two close places from being blown up to fill the map. */
export function frameAround(points: readonly Coordinates[], minimumHalfExtent = 1): Frame {
  const lats = points.map((point) => point.lat);
  const lons = points.map((point) => point.lon);
  const centre = {
    lat: (Math.min(...lats) + Math.max(...lats)) / 2,
    lon: (Math.min(...lons) + Math.max(...lons)) / 2,
  };
  const corner = offsetInMetres(centre, { lat: Math.max(...lats), lon: Math.max(...lons) });
  return {
    centre,
    halfWidth: Math.max(corner.east, minimumHalfExtent),
    halfHeight: Math.max(corner.north, minimumHalfExtent),
  };
}

/** One scale for both axes, so distances on the drawing keep their real proportions. */
export function scaleOf(frame: Frame, canvas: Canvas): number {
  return Math.min(
    (canvas.width / 2 - canvas.padding) / frame.halfWidth,
    (canvas.height / 2 - canvas.padding) / frame.halfHeight,
  );
}

export function project(
  frame: Frame,
  point: Coordinates,
  canvas: Canvas,
): { x: number; y: number } {
  const offset = offsetInMetres(frame.centre, point);
  const scale = scaleOf(frame, canvas);
  return {
    x: canvas.width / 2 + offset.east * scale,
    y: canvas.height / 2 - offset.north * scale,
  };
}
