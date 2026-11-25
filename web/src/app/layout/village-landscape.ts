import { Component } from '@angular/core';

/**
 * Decorative drawing of the village. Phones get their own composition (castle centred)
 * because cropping the wide one cut the castle at the edge.
 */
@Component({
  selector: 'app-village-landscape',
  host: { 'aria-hidden': 'true', class: 'block' },
  template: `
    <svg
      viewBox="0 0 400 180"
      preserveAspectRatio="xMidYMax slice"
      focusable="false"
      class="block h-40 w-full sm:hidden"
    >
      <circle cx="322" cy="46" r="24" class="fill-primary/25" />
      <path d="M0 112 C 70 80 150 96 210 86 S 330 60 400 84 V180 H0 Z" class="fill-line" />
      <g class="fill-muted/60">
        <rect x="130" y="58" width="90" height="36" />
        <rect x="118" y="42" width="22" height="52" />
        <rect x="210" y="46" width="22" height="48" />
        <rect x="118" y="36" width="6" height="7" />
        <rect x="126" y="36" width="6" height="7" />
        <rect x="134" y="36" width="6" height="7" />
        <rect x="210" y="40" width="6" height="7" />
        <rect x="218" y="40" width="6" height="7" />
        <rect x="226" y="40" width="6" height="7" />
        <rect x="144" y="52" width="7" height="7" />
        <rect x="160" y="52" width="7" height="7" />
        <rect x="176" y="52" width="7" height="7" />
        <rect x="192" y="52" width="7" height="7" />
      </g>
      <path
        d="M0 132 C 80 108 160 118 240 104 S 350 100 400 112 V180 H0 Z"
        class="fill-accent/35"
      />
      <g class="fill-muted/70">
        <rect x="282" y="80" width="18" height="34" />
        <path d="M279 82 L291 62 L303 82 Z" />
        <rect x="300" y="96" width="34" height="18" />
      </g>
      <path
        d="M0 152 C 90 134 180 148 280 138 S 360 134 400 140 V180 H0 Z"
        class="fill-accent/55"
      />
      <path d="M0 170 C 100 158 220 176 320 164 S 380 162 400 168 V180 H0 Z" class="fill-sunk" />
      <g class="fill-accent">
        <circle cx="50" cy="140" r="10" />
        <circle cx="72" cy="146" r="7" />
        <circle cx="358" cy="134" r="9" />
      </g>
    </svg>

    <svg
      viewBox="0 0 1200 240"
      preserveAspectRatio="xMidYMax slice"
      focusable="false"
      class="hidden h-52 w-full sm:block"
    >
      <circle cx="930" cy="78" r="44" class="fill-primary/25" />

      <path
        d="M0 150 C 160 95 300 120 430 105 S 700 70 860 110 S 1080 95 1200 120 V240 H0 Z"
        class="fill-line"
      />

      <g class="fill-muted/60">
        <rect x="300" y="62" width="150" height="60" />
        <rect x="285" y="40" width="34" height="82" />
        <rect x="431" y="48" width="34" height="74" />
        <rect x="285" y="32" width="8" height="10" />
        <rect x="298" y="32" width="8" height="10" />
        <rect x="311" y="32" width="8" height="10" />
        <rect x="431" y="40" width="8" height="10" />
        <rect x="444" y="40" width="8" height="10" />
        <rect x="457" y="40" width="8" height="10" />
        <rect x="300" y="54" width="10" height="10" />
        <rect x="322" y="54" width="10" height="10" />
        <rect x="344" y="54" width="10" height="10" />
        <rect x="366" y="54" width="10" height="10" />
        <rect x="388" y="54" width="10" height="10" />
        <rect x="410" y="54" width="10" height="10" />
      </g>

      <path
        d="M0 175 C 140 140 260 150 380 128 S 620 120 760 140 S 1010 118 1200 150 V240 H0 Z"
        class="fill-accent/35"
      />

      <g class="fill-muted/70">
        <rect x="742" y="88" width="30" height="58" />
        <path d="M738 90 L757 58 L776 90 Z" />
        <rect x="772" y="112" width="58" height="34" />
      </g>

      <path
        d="M0 205 C 180 178 320 196 500 182 S 820 170 980 190 S 1120 182 1200 188 V240 H0 Z"
        class="fill-accent/55"
      />

      <path d="M0 228 C 220 205 420 232 640 214 S 1000 206 1200 224 V240 H0 Z" class="fill-sunk" />

      <g class="fill-accent">
        <circle cx="118" cy="182" r="15" />
        <circle cx="152" cy="190" r="11" />
        <circle cx="560" cy="176" r="13" />
        <circle cx="1040" cy="178" r="16" />
        <circle cx="1074" cy="186" r="10" />
      </g>
    </svg>
  `,
})
export class VillageLandscape {}
