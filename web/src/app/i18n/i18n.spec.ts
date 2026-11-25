import { TestBed } from '@angular/core/testing';
import { I18n } from './i18n';

describe('I18n', () => {
  beforeEach(() => localStorage.clear());

  it('starts in Spanish and marks the document as Spanish', () => {
    const i18n = TestBed.inject(I18n);

    expect(i18n.language()).toBe('es');
    expect(i18n.texts().nav.pois).toBe('Puntos de interés');
    TestBed.tick();
    expect(document.documentElement.lang).toBe('es');
  });

  it('switches every text and the document language at once', () => {
    const i18n = TestBed.inject(I18n);

    i18n.use('en');
    TestBed.tick();

    expect(i18n.texts().nav.pois).toBe('Points of interest');
    expect(document.documentElement.lang).toBe('en');
  });

  it('remembers the chosen language', () => {
    TestBed.inject(I18n).use('en');
    TestBed.resetTestingModule();

    expect(TestBed.inject(I18n).language()).toBe('en');
  });
});
