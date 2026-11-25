import { Component, computed, inject, input } from '@angular/core';
import { NgTemplateOutlet } from '@angular/common';
import { RouterLink } from '@angular/router';
import { I18n } from '../i18n/i18n';
import { Poi } from './poi';
import { accessibilityText, openNowText } from './poi-labels';

/** The one card for the list and the assistant (D-031). Unknown states are said in words. */
@Component({
  selector: 'app-poi-card',
  imports: [NgTemplateOutlet, RouterLink],
  template: `
    @let texts = i18n.texts();
    @let place = poi();
    <article
      class="relative flex h-full flex-col rounded-2xl border border-line bg-surface p-5 shadow-sm transition-[translate,box-shadow] hover:-translate-y-0.5 hover:shadow-md"
    >
      <ng-template #name>
        <!-- The link covers the whole card, so the card is one click target and one tab stop. -->
        <a
          class="text-text no-underline after:absolute after:inset-0 after:rounded-2xl hover:text-primary"
          [routerLink]="['/pois', place.id]"
          [attr.lang]="nameLanguage()"
          >{{ place.nombre.texto }}</a
        >
      </ng-template>
      @if (headingLevel() === 3) {
        <h3 class="text-xl font-semibold"><ng-container [ngTemplateOutlet]="name" /></h3>
      } @else {
        <h2 class="text-xl font-semibold"><ng-container [ngTemplateOutlet]="name" /></h2>
      }
      <dl class="order-first mb-1.5">
        <dt class="sr-only">{{ texts.poi.category }}</dt>
        <dd class="text-xs font-semibold tracking-[0.12em] text-accent uppercase">
          {{ texts.categories[place.categoria] }}
        </dd>
      </dl>
      <dl class="mt-auto flex flex-wrap gap-2 pt-4 text-sm">
        <div class="inline-flex items-center rounded-full bg-sunk px-3 py-1">
          <dt class="sr-only">{{ texts.poi.openNow }}</dt>
          <dd class="inline-flex items-center gap-2">
            <span aria-hidden="true" class="size-2 rounded-full" [class]="openDot()"></span>
            {{ openNow() }}
          </dd>
        </div>
        <div class="inline-flex items-center rounded-full bg-sunk px-3 py-1">
          <dt class="sr-only">{{ texts.poi.accessibility }}</dt>
          <dd>{{ accessibility() }}</dd>
        </div>
        <div class="inline-flex items-center rounded-full bg-sunk px-3 py-1">
          <dt class="sr-only">{{ texts.poi.price }}</dt>
          <dd>{{ place.precio.texto }}</dd>
        </div>
      </dl>
    </article>
  `,
})
export class PoiCard {
  readonly poi = input.required<Poi>();
  /** 2 on a page of cards; 3 when the cards sit under a section heading. */
  readonly headingLevel = input<2 | 3>(2);
  protected readonly i18n = inject(I18n);

  protected readonly nameLanguage = computed(() => {
    const served = this.poi().nombre.idioma;
    return served === this.i18n.language() ? null : served;
  });

  protected readonly accessibility = computed(() =>
    accessibilityText(this.poi().accesible, this.i18n.texts()),
  );
  /** Decorative only: the state is always written next to it. */
  protected readonly openDot = computed(() => {
    const open = this.poi().abierto_ahora;
    if (open === null) {
      return 'border border-muted';
    }
    return open ? 'bg-accent' : 'bg-muted';
  });
  protected readonly openNow = computed(() =>
    openNowText(this.poi().abierto_ahora, this.i18n.texts()),
  );
}
