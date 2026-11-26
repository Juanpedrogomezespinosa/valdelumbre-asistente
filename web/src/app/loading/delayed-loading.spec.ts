import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { delayedLoading } from './delayed-loading';

describe('delayedLoading', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('only reports a load that lasts longer than 300 ms, so quick loads never flash', () => {
    const loading = signal(true);
    const slow = TestBed.runInInjectionContext(() => delayedLoading(loading));
    TestBed.tick();

    vi.advanceTimersByTime(299);
    expect(slow()).toBe(false);

    vi.advanceTimersByTime(1);
    expect(slow()).toBe(true);
  });

  it('stops reporting as soon as the load ends', () => {
    const loading = signal(true);
    const slow = TestBed.runInInjectionContext(() => delayedLoading(loading));
    TestBed.tick();
    vi.advanceTimersByTime(300);

    loading.set(false);
    TestBed.tick();

    expect(slow()).toBe(false);
  });

  it('never reports a load that ends before the delay', () => {
    const loading = signal(true);
    const slow = TestBed.runInInjectionContext(() => delayedLoading(loading));
    TestBed.tick();
    vi.advanceTimersByTime(200);

    loading.set(false);
    TestBed.tick();
    vi.advanceTimersByTime(500);

    expect(slow()).toBe(false);
  });
});
