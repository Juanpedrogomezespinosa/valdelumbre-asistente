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
    <article class="h-full rounded-lg border border-control-border bg-surface p-4">
      <ng-template #name>
        <a [routerLink]="['/pois', place.id]" [attr.lang]="nameLanguage()">{{
          place.nombre.texto
        }}</a>
      </ng-template>
      @if (headingLevel() === 3) {
        <h3 class="mb-3 text-lg font-semibold"><ng-container [ngTemplateOutlet]="name" /></h3>
      } @else {
        <h2 class="mb-3 text-lg font-semibold"><ng-container [ngTemplateOutlet]="name" /></h2>
      }
      <dl class="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
        <dt class="text-muted">{{ texts.poi.category }}</dt>
        <dd>{{ texts.categories[place.categoria] }}</dd>
        <dt class="text-muted">{{ texts.poi.accessibility }}</dt>
        <dd>{{ accessibility() }}</dd>
        <dt class="text-muted">{{ texts.poi.openNow }}</dt>
        <dd>{{ openNow() }}</dd>
        <dt class="text-muted">{{ texts.poi.price }}</dt>
        <dd>{{ place.precio.texto }}</dd>
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
  protected readonly openNow = computed(() =>
    openNowText(this.poi().abierto_ahora, this.i18n.texts()),
  );
}
