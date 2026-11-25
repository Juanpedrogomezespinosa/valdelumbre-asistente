import { Component, inject } from '@angular/core';
import { I18n } from '../../i18n/i18n';
import { PageHeading } from '../../layout/page-heading';

@Component({
  selector: 'app-poi-list-page',
  imports: [PageHeading],
  template: `<app-page-heading>{{ i18n.texts().pages.pois }}</app-page-heading>`,
})
export class PoiListPage {
  protected readonly i18n = inject(I18n);
}
