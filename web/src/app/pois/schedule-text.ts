import { Texts } from '../i18n/texts';
import { Season, Slot } from './poi';

const ALL_WEEK = 7;
/** Runs of at least this many days read as a range ("lunes a miércoles"), shorter ones as a list. */
const MIN_RANGE = 3;

/** ISO weekdays (1 = Monday, D-010) in words: "martes a domingo", "viernes y sábado". */
export function daysText(days: number[], texts: Texts): string {
  const sorted = [...new Set(days)].sort((a, b) => a - b);
  const schedule = texts.schedule;
  if (sorted.length === ALL_WEEK) {
    return schedule.everyDay;
  }
  const name = (day: number) => schedule.weekdays[day - 1];
  const items = consecutiveRuns(sorted).flatMap((run) =>
    run.length >= MIN_RANGE
      ? [`${name(run[0])} ${schedule.through} ${name(run[run.length - 1])}`]
      : run.map(name),
  );
  return joinAsList(items, schedule.and);
}

export function seasonText(season: Season, texts: Texts): string {
  return texts.schedule.season(dayOfMonth(season.desde, texts), dayOfMonth(season.hasta, texts));
}

export function slotText(slot: Slot, texts: Texts): string {
  const sentence = `${capitalize(daysText(slot.dias, texts))}, ${texts.schedule.hours(slot.abre, slot.cierra)}`;
  return slot.temporada ? `${sentence} (${seasonText(slot.temporada, texts)})` : sentence;
}

function consecutiveRuns(sorted: number[]): number[][] {
  const runs: number[][] = [];
  for (const day of sorted) {
    const last = runs.at(-1);
    if (last && day === last[last.length - 1] + 1) {
      last.push(day);
    } else {
      runs.push([day]);
    }
  }
  return runs;
}

function joinAsList(items: string[], and: string): string {
  return items.length <= 1
    ? items.join('')
    : `${items.slice(0, -1).join(', ')} ${and} ${items[items.length - 1]}`;
}

/** The API sends seasons as "MM-DD". */
function dayOfMonth(monthDay: string, texts: Texts): string {
  const [month, day] = monthDay.split('-').map(Number);
  return texts.schedule.dayOfMonth(day, texts.schedule.months[month - 1]);
}

function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
