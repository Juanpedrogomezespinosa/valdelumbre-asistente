import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { I18n } from '../../i18n/i18n';
import { PageHeading } from '../../layout/page-heading';

@Component({
  selector: 'app-not-found-page',
  imports: [PageHeading, RouterLink],
  template: `
    <app-page-heading>{{ i18n.texts().pages.notFound }}</app-page-heading>
    <p class="mb-4">{{ i18n.texts().notFound.message }}</p>
    <a routerLink="/">{{ i18n.texts().notFound.backHome }}</a>
  `,
})
export class NotFoundPage {
  protected readonly i18n = inject(I18n);
}
