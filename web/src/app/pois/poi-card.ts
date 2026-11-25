import { Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { I18n } from '../i18n/i18n';
import { Poi } from './poi';

/** The one card for the list and the assistant (D-031). Unknown states are said in words. */
@Component({
  selector: 'app-poi-card',
  imports: [RouterLink],
  template: `
    @let texts = i18n.texts();
    @let place = poi();
    <article class="h-full rounded-lg border border-control-border bg-surface p-4">
      <h2 class="mb-3 text-lg font-semibold">
        <a [routerLink]="['/pois', place.id]" [attr.lang]="nameLanguage()">{{
          place.nombre.texto
        }}</a>
      </h2>
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
  protected readonly i18n = inject(I18n);

  protected readonly nameLanguage = computed(() => {
    const served = this.poi().nombre.idioma;
    return served === this.i18n.language() ? null : served;
  });

  protected readonly accessibility = computed(() => {
    const texts = this.i18n.texts().poi;
    const accessible = this.poi().accesible;
    if (accessible === null) {
      return texts.accessibilityUnknown;
    }
    return accessible ? texts.accessible : texts.notAccessible;
  });

  protected readonly openNow = computed(() => {
    const texts = this.i18n.texts().poi;
    const open = this.poi().abierto_ahora;
    if (open === null) {
      return texts.hoursUnknown;
    }
    return open ? texts.open : texts.closed;
  });
}
