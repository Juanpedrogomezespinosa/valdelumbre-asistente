import { compassPoint, frameAround, offsetInMetres, project } from './map-geometry';

const PLAZA = { lat: 40.4168, lon: -3.7038 };

describe('offsetInMetres', () => {
  it('measures east and north from an origin, in metres', () => {
    const offset = offsetInMetres(PLAZA, { lat: 40.4178, lon: -3.7038 });

    expect(offset.north).toBeCloseTo(111, 0);
    expect(offset.east).toBeCloseTo(0, 5);
  });

  it('shrinks longitude degrees with latitude', () => {
    const offset = offsetInMetres(PLAZA, { lat: 40.4168, lon: -3.7028 });

    // 0.001° of longitude at 40.4° N is about 85 m, not 111 m.
    expect(offset.east).toBeCloseTo(85, 0);
  });
});

describe('compassPoint', () => {
  it.each([
    [{ east: 0, north: 100 }, 0],
    [{ east: 100, north: 100 }, 1],
    [{ east: 100, north: 0 }, 2],
    [{ east: 0, north: -100 }, 4],
    [{ east: -100, north: 0 }, 6],
    [{ east: -100, north: 100 }, 7],
  ])('turns %o into one of eight points (0 = north, clockwise)', (offset, expected) => {
    expect(compassPoint(offset)).toBe(expected);
  });
});

describe('project', () => {
  const frame = frameAround([
    { lat: 40.41, lon: -3.71 },
    { lat: 40.42, lon: -3.7 },
  ]);

  it('puts north at the top and west on the left, inside the padding', () => {
    const northWest = project(
      frame,
      { lat: 40.42, lon: -3.71 },
      { width: 400, height: 400, padding: 20 },
    );
    const southEast = project(
      frame,
      { lat: 40.41, lon: -3.7 },
      { width: 400, height: 400, padding: 20 },
    );

    expect(northWest.x).toBeLessThan(southEast.x);
    expect(northWest.y).toBeLessThan(southEast.y);
    for (const point of [northWest, southEast]) {
      expect(point.x).toBeGreaterThanOrEqual(20);
      expect(point.x).toBeLessThanOrEqual(380);
      expect(point.y).toBeGreaterThanOrEqual(20);
      expect(point.y).toBeLessThanOrEqual(380);
    }
  });

  it('keeps real proportions: one scale for both axes', () => {
    const size = { width: 400, height: 400, padding: 0 };
    const a = project(frame, { lat: 40.41, lon: -3.71 }, size);
    const b = project(frame, { lat: 40.42, lon: -3.7 }, size);

    // 0.01° north is ~1110 m and 0.01° east ~850 m here, so the drawing is taller than wide.
    expect(Math.abs(a.y - b.y)).toBeGreaterThan(Math.abs(a.x - b.x));
  });
});
