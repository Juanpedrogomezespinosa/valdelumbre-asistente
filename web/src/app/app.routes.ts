import { Routes } from '@angular/router';
import { AssistantPage } from './pages/assistant/assistant-page';
import { NotFoundPage } from './pages/not-found/not-found-page';
import { PoiDetailPage } from './pages/poi-detail/poi-detail-page';
import { PoiListPage } from './pages/poi-list/poi-list-page';

// Each `title` is a page key: PageTitleStrategy turns it into the title in the active language.
export const routes: Routes = [
  { path: '', component: AssistantPage, title: 'assistant' },
  { path: 'pois', component: PoiListPage, title: 'pois' },
  { path: 'pois/:id', component: PoiDetailPage, title: 'poiDetail' },
  { path: '**', component: NotFoundPage, title: 'notFound' },
];
