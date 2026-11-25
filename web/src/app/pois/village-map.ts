import {
  Component,
  ElementRef,
  computed,
  inject,
  input,
  linkedSignal,
  signal,
  viewChild,
} from '@angular/core';
import { I18n } from '../i18n/i18n';
import { CATEGORY_GLYPHS } from './category-glyph';
import { Canvas, Coordinates, frameAround, project, scaleOf } from './map-geometry';
import {
  Point,
  Viewport,
  centredOn,
  fractionInView,
  panBy,
  viewBoxOf,
  wholeMap,
  zoomAt,
} from './map-viewport';
import { Poi } from './poi';
import { PoiCard } from './poi-card';
import { LANDMARK_ID } from './relative-location';

const CANVAS: Canvas = { width: 1000, height: 625, padding: 70 };
const MINIMUM_HALF_EXTENT_METRES = 400;
const SCALE_STEPS_METRES = [25, 50, 100, 200, 250, 500, 1000, 2000];
// The old town: most places are 100-600 m from Plaza Mayor, the rest 2-3 km away.
const CENTRE_RADIUS_METRES = 600;
const CENTRE_ZOOM = 3.5;
const ZOOM_STEP = 1.5;
const KEY_PAN_FRACTION = 0.15;
// Movement (px) below which a press on a marker is a click, not the start of a drag.
const DRAG_THRESHOLD = 4;
const GRID_STEP = 50;
const WHEEL_SENSITIVITY = 0.0025;

interface Marker {
  poi: Poi;
  point: Point;
  label: string;
  glyph: string;
  left: number;
  top: number;
  selected: boolean;
  current: boolean;
}

type Located = Poi & { coordenadas: Coordinates };

/**
 * Own map (D-019, D-047): a decorative SVG background that pans and zooms through its
 * viewBox, and real HTML buttons on top as markers, so focus, names and touch targets are
 * the browser's. Mouse, touch, buttons and keyboard all move the same viewport.
 */
@Component({
  selector: 'app-village-map',
  imports: [PoiCard],
  templateUrl: './village-map.html',
})
export class VillageMap {
  readonly pois = input.required<readonly Poi[]>();
  /** Id of the place the page is about (the detail page). */
  readonly highlighted = input<string | null>(null);

  protected readonly i18n = inject(I18n);
  private readonly stage = viewChild.required<ElementRef<HTMLElement>>('stage');

  protected readonly located = computed(() =>
    this.pois().filter((poi): poi is Located => poi.coordenadas !== null),
  );
  protected readonly missing = computed(() => this.pois().length - this.located().length);

  private readonly frame = computed(() =>
    frameAround(
      this.located().map((poi) => poi.coordenadas),
      MINIMUM_HALF_EXTENT_METRES,
    ),
  );
  private readonly points = computed(
    () =>
      new Map(
        this.located().map((poi) => [poi.id, project(this.frame(), poi.coordenadas, CANVAS)]),
      ),
  );

  /** Starts close to the highlighted place when it is in the old town. */
  protected readonly view = linkedSignal<Viewport>(() => this.initialView());
  protected readonly selectedId = signal<string | null>(null);
  protected readonly selected = computed(
    () => this.located().find((poi) => poi.id === this.selectedId()) ?? null,
  );

  protected readonly viewBox = computed(() => {
    const box = viewBoxOf(this.view(), CANVAS);
    return `${box.x} ${box.y} ${box.width} ${box.height}`;
  });

  protected readonly markers = computed<Marker[]>(() => {
    const texts = this.i18n.texts();
    return this.located().map((poi) => {
      const point = this.points().get(poi.id) ?? { x: 0, y: 0 };
      const fraction = fractionInView(this.view(), point, CANVAS);
      return {
        poi,
        point,
        label: `${poi.nombre.texto}, ${texts.categories[poi.categoria]}`,
        glyph: CATEGORY_GLYPHS[poi.categoria],
        left: fraction.x * 100,
        top: fraction.y * 100,
        selected: poi.id === this.selectedId(),
        current: poi.id === this.highlighted(),
      };
    });
  });

  /** A round distance about a fifth of the visible width, as a bar of that width. */
  protected readonly scaleBar = computed(() => {
    const visibleMetres = viewBoxOf(this.view(), CANVAS).width / scaleOf(this.frame(), CANVAS);
    const metres =
      SCALE_STEPS_METRES.filter((step) => step <= visibleMetres / 5).at(-1) ??
      SCALE_STEPS_METRES[0];
    return { metres, width: (metres / visibleMetres) * 100 };
  });

  /** The old town drawn as a soft patch around Plaza Mayor, with decorative rings around it. */
  protected readonly oldTown = computed(() => {
    const square = this.points().get(LANDMARK_ID);
    return square
      ? { ...square, radius: CENTRE_RADIUS_METRES * scaleOf(this.frame(), CANVAS) }
      : null;
  });
  protected readonly contours = [1.5, 2.2, 3, 3.9, 4.9];
  protected readonly gridX = gridLines(CANVAS.width);
  protected readonly gridY = gridLines(CANVAS.height);
  protected readonly canvas = CANVAS;
  protected readonly zoomStep = ZOOM_STEP;

  private readonly pointers = new Map<number, Point>();
  private dragDistance = 0;

  protected select(poi: Poi): void {
    if (this.dragDistance > DRAG_THRESHOLD) {
      return;
    }
    this.selectedId.set(this.selectedId() === poi.id ? null : poi.id);
  }

  /** Tabbing to a marker outside the view brings it into view. */
  protected reveal(marker: Marker): void {
    if (marker.left < 5 || marker.left > 95 || marker.top < 8 || marker.top > 95) {
      this.view.set(centredOn(marker.point, this.view().zoom, CANVAS));
    }
  }

  protected zoomBy(factor: number): void {
    this.view.set(zoomAt(this.view(), factor, this.view().centre, CANVAS));
  }

  protected reset(): void {
    this.view.set(wholeMap(CANVAS));
  }

  protected onKey(event: KeyboardEvent): void {
    const box = viewBoxOf(this.view(), CANVAS);
    const step = { x: box.width * KEY_PAN_FRACTION, y: box.height * KEY_PAN_FRACTION };
    const moves: Record<string, () => void> = {
      ArrowLeft: () => this.pan({ x: -step.x, y: 0 }),
      ArrowRight: () => this.pan({ x: step.x, y: 0 }),
      ArrowUp: () => this.pan({ x: 0, y: -step.y }),
      ArrowDown: () => this.pan({ x: 0, y: step.y }),
      '+': () => this.zoomBy(ZOOM_STEP),
      '=': () => this.zoomBy(ZOOM_STEP),
      '-': () => this.zoomBy(1 / ZOOM_STEP),
      '0': () => this.reset(),
    };
    const move = moves[event.key];
    if (move) {
      event.preventDefault();
      move();
    }
  }

  protected onWheel(event: WheelEvent): void {
    event.preventDefault();
    // Proportional to how far the wheel turned: a mouse notch (~100) is ~1.3x, and the many
    // small steps of a trackpad add up smoothly instead of each one jumping a whole level.
    const factor = Math.exp(-Math.max(-200, Math.min(200, event.deltaY)) * WHEEL_SENSITIVITY);
    this.view.set(zoomAt(this.view(), factor, this.toMap(event), CANVAS));
  }

  protected onPointerDown(event: PointerEvent): void {
    this.pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    this.dragDistance = 0;
  }

  protected onPointerMove(event: PointerEvent): void {
    const previous = this.pointers.get(event.pointerId);
    if (!previous) {
      return;
    }
    const current = { x: event.clientX, y: event.clientY };
    if (this.pointers.size === 2) {
      this.pinch(event.pointerId, current);
    } else {
      const unitsPerPixel = this.unitsPerPixel();
      this.dragDistance += Math.hypot(current.x - previous.x, current.y - previous.y);
      if (this.dragDistance > DRAG_THRESHOLD) {
        // Captured only once it is really a drag, so a plain click still reaches the marker.
        this.stage().nativeElement.setPointerCapture?.(event.pointerId);
      }
      this.pan({
        x: -(current.x - previous.x) * unitsPerPixel,
        y: -(current.y - previous.y) * unitsPerPixel,
      });
    }
    this.pointers.set(event.pointerId, current);
  }

  protected onPointerUp(event: PointerEvent): void {
    this.pointers.delete(event.pointerId);
  }

  private pinch(movedId: number, moved: Point): void {
    const [first, second] = [...this.pointers.entries()].map(([id, point]) =>
      id === movedId ? { before: point, after: moved } : { before: point, after: point },
    );
    const before = Math.hypot(first.before.x - second.before.x, first.before.y - second.before.y);
    const after = Math.hypot(first.after.x - second.after.x, first.after.y - second.after.y);
    if (before > 0) {
      this.dragDistance += DRAG_THRESHOLD + 1;
      const middle = {
        clientX: (first.after.x + second.after.x) / 2,
        clientY: (first.after.y + second.after.y) / 2,
      };
      this.view.set(zoomAt(this.view(), after / before, this.toMap(middle), CANVAS));
    }
  }

  private pan(delta: Point): void {
    this.view.set(panBy(this.view(), delta, CANVAS));
  }

  private unitsPerPixel(): number {
    const width = this.stage().nativeElement.getBoundingClientRect().width || CANVAS.width;
    return viewBoxOf(this.view(), CANVAS).width / width;
  }

  private toMap(event: { clientX: number; clientY: number }): Point {
    const rect = this.stage().nativeElement.getBoundingClientRect();
    const box = viewBoxOf(this.view(), CANVAS);
    if (!rect.width || !rect.height) {
      return this.view().centre;
    }
    return {
      x: box.x + ((event.clientX - rect.left) / rect.width) * box.width,
      y: box.y + ((event.clientY - rect.top) / rect.height) * box.height,
    };
  }

  private initialView(): Viewport {
    const place = this.points().get(this.highlighted() ?? '');
    const landmark = this.points().get(LANDMARK_ID);
    if (!place || !landmark) {
      return wholeMap(CANVAS);
    }
    const metres =
      Math.hypot(place.x - landmark.x, place.y - landmark.y) / scaleOf(this.frame(), CANVAS);
    return metres <= CENTRE_RADIUS_METRES
      ? centredOn(place, CENTRE_ZOOM, CANVAS)
      : wholeMap(CANVAS);
  }
}

function gridLines(length: number): number[] {
  return Array.from({ length: Math.floor(length / GRID_STEP) }, (_, i) => (i + 1) * GRID_STEP);
}
