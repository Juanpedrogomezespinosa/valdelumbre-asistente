export interface Point {
  x: number;
  y: number;
}

export interface Size {
  width: number;
  height: number;
}

/** What part of the map is visible: a centre in map units and a zoom (1 = whole map). */
export interface Viewport {
  centre: Point;
  zoom: number;
}

export const MAX_ZOOM = 8;

export function wholeMap(size: Size): Viewport {
  return { centre: { x: size.width / 2, y: size.height / 2 }, zoom: 1 };
}

export function viewBoxOf(view: Viewport, size: Size): Size & Point {
  const width = size.width / view.zoom;
  const height = size.height / view.zoom;
  return { x: view.centre.x - width / 2, y: view.centre.y - height / 2, width, height };
}

/** Zoom by `factor` keeping `anchor` (map units, e.g. under the pointer) where it was. */
export function zoomAt(view: Viewport, factor: number, anchor: Point, size: Size): Viewport {
  const zoom = clamp(view.zoom * factor, 1, MAX_ZOOM);
  const kept = view.zoom / zoom;
  return keptInside(
    {
      centre: {
        x: anchor.x - (anchor.x - view.centre.x) * kept,
        y: anchor.y - (anchor.y - view.centre.y) * kept,
      },
      zoom,
    },
    size,
  );
}

export function panBy(view: Viewport, delta: Point, size: Size): Viewport {
  return keptInside(
    { centre: { x: view.centre.x + delta.x, y: view.centre.y + delta.y }, zoom: view.zoom },
    size,
  );
}

export function centredOn(point: Point, zoom: number, size: Size): Viewport {
  return keptInside({ centre: point, zoom: clamp(zoom, 1, MAX_ZOOM) }, size);
}

/** 0–1 when the point is visible; outside that range when it is off screen. */
export function fractionInView(view: Viewport, point: Point, size: Size): Point {
  const box = viewBoxOf(view, size);
  return { x: (point.x - box.x) / box.width, y: (point.y - box.y) / box.height };
}

/** The view never shows anything beyond the edges of the map. */
function keptInside(view: Viewport, size: Size): Viewport {
  const halfWidth = size.width / view.zoom / 2;
  const halfHeight = size.height / view.zoom / 2;
  return {
    centre: {
      x: clamp(view.centre.x, halfWidth, size.width - halfWidth),
      y: clamp(view.centre.y, halfHeight, size.height - halfHeight),
    },
    zoom: view.zoom,
  };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}
