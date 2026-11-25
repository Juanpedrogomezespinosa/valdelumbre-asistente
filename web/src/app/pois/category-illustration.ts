import { Component, input } from '@angular/core';
import { Category } from './poi';

/**
 * Decorative drawing for a category. The catalogue has no photos, and a stock photo would
 * pass for the real place, so each detail page gets an illustration of its kind instead.
 */
@Component({
  selector: 'app-category-illustration',
  host: { 'aria-hidden': 'true', class: 'block' },
  template: `
    <svg
      viewBox="0 0 960 200"
      preserveAspectRatio="xMidYMax slice"
      focusable="false"
      class="block h-40 w-full sm:h-48"
    >
      <path d="M0 148 C 200 112 420 140 600 118 S 860 108 960 124 V200 H0 Z" class="fill-line" />
      <!-- The scene is drawn on a 480-wide stage, centred, so phones crop only empty sides. -->
      <g transform="translate(240 20)">
        <circle cx="400" cy="52" r="26" class="fill-primary/25" />
        @switch (category()) {
          @case ('monumento') {
            <g class="fill-muted/70">
              <rect x="170" y="62" width="140" height="48" />
              <rect x="156" y="40" width="30" height="70" />
              <rect x="294" y="44" width="30" height="66" />
              @for (x of [156, 167, 178, 294, 305, 316]; track x) {
                <rect [attr.x]="x" [attr.y]="x < 290 ? 32 : 36" width="8" height="9" />
              }
              @for (x of [194, 214, 234, 254, 274]; track x) {
                <rect [attr.x]="x" y="54" width="10" height="9" />
              }
              <path d="M226 110 V88 a14 14 0 0 1 28 0 V110 Z" class="fill-sunk" />
            </g>
          }
          @case ('museo') {
            <g class="fill-muted/70">
              <path d="M160 64 L240 30 L320 64 Z" />
              <rect x="164" y="66" width="152" height="8" />
              @for (x of [174, 204, 234, 264, 294]; track x) {
                <rect [attr.x]="x" y="78" width="12" height="34" />
              }
              <rect x="156" y="112" width="168" height="8" />
            </g>
          }
          @case ('naturaleza') {
            <path d="M60 130 L150 50 L240 130 Z" class="fill-accent/35" />
            <path d="M190 130 L280 70 L370 130 Z" class="fill-accent/45" />
            @for (
              tree of [
                [110, 112],
                [140, 120],
                [330, 116],
                [360, 122],
              ];
              track $index
            ) {
              <rect
                [attr.x]="tree[0] - 2"
                [attr.y]="tree[1]"
                width="4"
                height="14"
                class="fill-muted/70"
              />
              <circle [attr.cx]="tree[0]" [attr.cy]="tree[1] - 6" r="13" class="fill-accent" />
            }
          }
          @case ('ruta') {
            <path
              d="M60 176 C 140 150 120 130 200 122 S 300 112 330 96 S 380 82 400 78"
              class="fill-none stroke-primary/60"
              stroke-width="6"
              stroke-dasharray="14 10"
              stroke-linecap="round"
            />
            <g class="fill-muted/70">
              <rect x="286" y="60" width="5" height="54" />
              <path d="M291 62 H340 L350 70 L340 78 H291 Z" />
            </g>
            <circle cx="120" cy="112" r="14" class="fill-accent" />
          }
          @case ('gastronomia') {
            <g class="fill-muted/70">
              <rect x="196" y="52" width="26" height="62" rx="6" />
              <rect x="202" y="30" width="14" height="26" rx="3" />
              <path d="M246 70 h40 c0 26 -10 36 -20 36 s-20 -10 -20 -36 z" />
              <rect x="264" y="104" width="4" height="12" />
              <rect x="252" y="114" width="28" height="4" rx="2" />
            </g>
            @for (
              olive of [
                [150, 96],
                [166, 86],
                [318, 94],
              ];
              track $index
            ) {
              <ellipse
                [attr.cx]="olive[0]"
                [attr.cy]="olive[1]"
                rx="7"
                ry="10"
                class="fill-accent"
              />
            }
          }
          @case ('servicio') {
            <g class="fill-muted/70">
              <rect x="196" y="40" width="88" height="70" rx="12" />
              <rect x="236" y="110" width="8" height="20" />
            </g>
            <circle cx="240" cy="58" r="6" class="fill-sunk" />
            <rect x="234" y="70" width="12" height="28" rx="3" class="fill-sunk" />
          }
          @case ('espacio_publico') {
            <g class="fill-muted/70">
              <rect x="120" y="58" width="240" height="56" />
              @for (x of [138, 178, 218, 258, 298]; track x) {
                <path [attr.d]="'M' + x + ' 114 V84 a14 14 0 0 1 28 0 V114 Z'" class="fill-sunk" />
              }
            </g>
            <ellipse cx="240" cy="132" rx="46" ry="8" class="fill-primary/30" />
          }
        }
      </g>
      <path d="M0 170 C 280 150 600 178 960 160 V200 H0 Z" class="fill-accent/55" />
      <path d="M0 190 C 320 176 640 198 960 184 V200 H0 Z" class="fill-sunk" />
    </svg>
  `,
})
export class CategoryIllustration {
  readonly category = input.required<Category>();
}
