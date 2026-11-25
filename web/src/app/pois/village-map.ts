import { Component, computed, inject, input, linkedSignal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { I18n } from '../i18n/i18n';
import {
  Canvas,
  Coordinates,
  distanceInMetres,
  frameAround,
  offsetInMetres,
  project,
  scaleOf,
} from './map-geometry';
import { Poi } from './poi';
import { LANDMARK_ID } from './relative-location';

const CANVAS: Canvas = { width: 400, height: 440, padding: 40 };
const MINIMUM_HALF_EXTENT_METRES = 400;
const SCALE_STEPS_METRES = [100, 200, 250, 500, 1000, 2000, 5000];
// The old town: everything within a short walk of Plaza Mayor (most places are 100-600 m away).
const CENTRE_RADIUS_METRES = 600;

interface PlacedPoint {
  poi: Poi;
  x: number;
  y: number;
  current: boolean;
  labelAnchor: 'start' | 'middle' | 'end';
}

/**
 * Own SVG map (D-019): complements the list, never replaces it. Each place is a link with
 * its name; places without coordinates are counted in words below the map.
 */
@Component({
  selector: 'app-village-map',
  imports: [RouterLink],
  template: `
    @let texts = i18n.texts().location;
    @if (landmark()) {
      <div class="mb-2 flex justify-end">
        <button
          type="button"
          class="rounded-full border border-control-border bg-surface px-3 py-1 text-sm hover:border-primary hover:text-primary aria-pressed:border-primary aria-pressed:font-semibold aria-pressed:text-primary"
          [attr.aria-pressed]="zoomedIn()"
          (click)="zoomed.set(!zoomed())"
        >
          {{ texts.zoomCentre }}
        </button>
      </div>
    }
    @if (placed().length > 0) {
      <svg
        role="group"
        [attr.aria-label]="texts.mapLabel"
        [attr.viewBox]="viewBox"
        class="block h-auto w-full rounded-2xl bg-sunk"
      >
        <g aria-hidden="true">
          @for (offset of grid(); track offset) {
            <line
              [attr.x1]="canvas.width / 2 + offset"
              y1="0"
              [attr.x2]="canvas.width / 2 + offset"
              [attr.y2]="canvas.height"
              class="stroke-line"
            />
            <line
              x1="0"
              [attr.y1]="canvas.height / 2 + offset"
              [attr.x2]="canvas.width"
              [attr.y2]="canvas.height / 2 + offset"
              class="stroke-line"
            />
          }
          <g [attr.transform]="'translate(' + (canvas.width - 28) + ' 34)'" class="fill-muted">
            <path d="M0 -18 L8 6 L0 1 L-8 6 Z" />
            <text y="22" text-anchor="middle" class="text-[13px] font-semibold">
              {{ texts.north }}
            </text>
          </g>
          <g
            [attr.transform]="
              'translate(' +
              (canvas.width - 20 - scaleBar().pixels) +
              ' ' +
              (canvas.height - 22) +
              ')'
            "
          >
            <line
              x1="0"
              y1="0"
              [attr.x2]="scaleBar().pixels"
              y2="0"
              class="stroke-muted"
              stroke-width="3"
            />
            <text
              [attr.x]="scaleBar().pixels"
              y="-8"
              text-anchor="end"
              class="fill-muted text-[12px]"
            >
              {{ texts.scale(scaleBar().metres) }}
            </text>
          </g>
        </g>

        @for (point of placed(); track point.poi.id) {
          <a
            class="group outline-none"
            [routerLink]="['/pois', point.poi.id]"
            [attr.aria-label]="point.poi.nombre.texto"
            [attr.aria-current]="point.current ? 'location' : null"
          >
            <!-- A bigger, invisible target for pointer and touch. -->
            <circle [attr.cx]="point.x" [attr.cy]="point.y" r="16" fill="transparent" />
            @if (point.current) {
              <circle [attr.cx]="point.x" [attr.cy]="point.y" r="17" class="fill-primary/25" />
            }
            <!-- The focus ring replaces the outline, which browsers draw unevenly on SVG links. -->
            <circle
              [attr.cx]="point.x"
              [attr.cy]="point.y"
              [attr.r]="point.current ? 9 : 7"
              class="fill-primary stroke-surface group-focus-visible:stroke-focus"
              stroke-width="2.5"
            />
            <text
              [attr.x]="point.x"
              [attr.y]="point.y - 15"
              [attr.text-anchor]="point.labelAnchor"
              paint-order="stroke"
              stroke-width="4"
              stroke-linejoin="round"
              class="pointer-events-none fill-text stroke-sunk text-[13px] font-semibold opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100"
              [class.opacity-100]="point.current"
            >
              {{ point.poi.nombre.texto }}
            </text>
          </a>
        }
      </svg>
    }
    @if (outsideView() > 0) {
      <p class="mt-2 text-sm text-muted">{{ texts.outsideView(outsideView()) }}</p>
    }
    @if (missing() > 0) {
      <p class="mt-2 text-sm text-muted">{{ texts.notOnMap(missing()) }}</p>
    }
  `,
})
export class VillageMap {
  readonly pois = input.required<readonly Poi[]>();
  /** Id of the place the map is about (the detail page), drawn bigger and labelled. */
  readonly highlighted = input<string | null>(null);

  protected readonly i18n = inject(I18n);
  protected readonly canvas = CANVAS;
  protected readonly viewBox = `0 0 ${CANVAS.width} ${CANVAS.height}`;

  private readonly located = computed(() =>
    this.pois().filter(
      (poi): poi is Poi & { coordenadas: Coordinates } => poi.coordenadas !== null,
    ),
  );
  protected readonly missing = computed(() => this.pois().length - this.located().length);

  protected readonly landmark = computed(
    () => this.located().find((poi) => poi.id === LANDMARK_ID) ?? null,
  );
  /** Zoomed in from the start when the page is about a place in the old town. */
  protected readonly zoomed = linkedSignal(() => {
    const landmark = this.landmark();
    const place = this.located().find((poi) => poi.id === this.highlighted());
    return landmark !== null && place !== undefined && inCentre(landmark, place);
  });
  /** Only zoomed while the square is shown: filters may leave it out. */
  protected readonly zoomedIn = computed(() => this.zoomed() && this.landmark() !== null);

  private readonly frame = computed(() => {
    const landmark = this.landmark();
    const framed =
      this.zoomedIn() && landmark
        ? this.located().filter((poi) => inCentre(landmark, poi))
        : this.located();
    return frameAround(
      framed.map((poi) => poi.coordenadas),
      MINIMUM_HALF_EXTENT_METRES,
    );
  });

  protected readonly placed = computed<PlacedPoint[]>(() =>
    this.located()
      .map((poi) => {
        const { x, y } = project(this.frame(), poi.coordenadas, CANVAS);
        return { poi, x, y, current: poi.id === this.highlighted(), labelAnchor: anchorFor(x) };
      })
      .filter(({ x, y }) => x >= 0 && x <= CANVAS.width && y >= 0 && y <= CANVAS.height),
  );
  protected readonly outsideView = computed(() => this.located().length - this.placed().length);

  /** The longest round distance that fits in a third of the map. */
  protected readonly scaleBar = computed(() => {
    const pixelsPerMetre = scaleOf(this.frame(), CANVAS);
    const fitting = SCALE_STEPS_METRES.filter(
      (metres) => metres * pixelsPerMetre <= CANVAS.width / 3,
    );
    const metres = fitting.at(-1) ?? SCALE_STEPS_METRES[0];
    return { metres, pixels: metres * pixelsPerMetre };
  });

  /** Decorative grid lines, one scale-bar length apart, from the centre outwards. */
  protected readonly grid = computed(() => {
    const step = this.scaleBar().pixels;
    const offsets: number[] = [];
    for (let offset = step; offset < CANVAS.height / 2; offset += step) {
      offsets.push(offset, -offset);
    }
    return [0, ...offsets];
  });
}

function inCentre(landmark: { coordenadas: Coordinates }, poi: { coordenadas: Coordinates }) {
  return (
    distanceInMetres(offsetInMetres(landmark.coordenadas, poi.coordenadas)) <= CENTRE_RADIUS_METRES
  );
}

function anchorFor(x: number): 'start' | 'middle' | 'end' {
  if (x < CANVAS.width * 0.25) {
    return 'start';
  }
  return x > CANVAS.width * 0.75 ? 'end' : 'middle';
}
