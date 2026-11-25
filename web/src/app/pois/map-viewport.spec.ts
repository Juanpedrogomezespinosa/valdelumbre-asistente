import {
  MAX_ZOOM,
  Viewport,
  centredOn,
  fractionInView,
  panBy,
  viewBoxOf,
  wholeMap,
  zoomAt,
} from './map-viewport';

const SIZE = { width: 1000, height: 600 };

describe('map viewport', () => {
  it('starts showing the whole map', () => {
    expect(viewBoxOf(wholeMap(SIZE), SIZE)).toEqual({ x: 0, y: 0, width: 1000, height: 600 });
  });

  it('zooms keeping the point under the pointer where it was', () => {
    const zoomed = zoomAt(wholeMap(SIZE), 2, { x: 250, y: 150 }, SIZE);

    expect(zoomed.zoom).toBe(2);
    expect(fractionInView(zoomed, { x: 250, y: 150 }, SIZE)).toEqual({ x: 0.25, y: 0.25 });
  });

  it('never zooms out beyond the whole map nor in beyond the maximum', () => {
    expect(zoomAt(wholeMap(SIZE), 0.5, { x: 500, y: 300 }, SIZE).zoom).toBe(1);
    expect(zoomAt(wholeMap(SIZE), 100, { x: 500, y: 300 }, SIZE).zoom).toBe(MAX_ZOOM);
  });

  it('pans, but never past the edge of the map', () => {
    const zoomed: Viewport = { centre: { x: 500, y: 300 }, zoom: 2 };

    expect(panBy(zoomed, { x: 100, y: 0 }, SIZE).centre).toEqual({ x: 600, y: 300 });
    expect(panBy(zoomed, { x: 10_000, y: -10_000 }, SIZE).centre).toEqual({ x: 750, y: 150 });
    expect(panBy(wholeMap(SIZE), { x: 100, y: 100 }, SIZE).centre).toEqual({ x: 500, y: 300 });
  });

  it('centres on a point as far as the edges allow', () => {
    expect(centredOn({ x: 400, y: 300 }, 2, SIZE).centre).toEqual({ x: 400, y: 300 });
    expect(centredOn({ x: 0, y: 0 }, 2, SIZE).centre).toEqual({ x: 250, y: 150 });
  });

  it('says where a point falls in the view, as a fraction of its size', () => {
    const view: Viewport = { centre: { x: 500, y: 300 }, zoom: 2 };

    expect(fractionInView(view, { x: 500, y: 300 }, SIZE)).toEqual({ x: 0.5, y: 0.5 });
    expect(fractionInView(view, { x: 0, y: 0 }, SIZE)).toEqual({ x: -0.5, y: -0.5 });
  });
});
