import { Component, computed, inject, signal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { forkJoin, of } from 'rxjs';
import { splitAnswer } from '../../assistant/answer-text';
import { AssistantService } from '../../assistant/assistant-service';
import { apiErrorDetail } from '../../http-error';
import { I18n } from '../../i18n/i18n';
import { PageHeading } from '../../layout/page-heading';
import { VillageLandscape } from '../../layout/village-landscape';
import { PoiCard } from '../../pois/poi-card';
import { PoisService } from '../../pois/pois-service';

const MAX_QUESTION_LENGTH = 500;

@Component({
  selector: 'app-assistant-page',
  imports: [PageHeading, PoiCard, VillageLandscape],
  templateUrl: './assistant-page.html',
})
export class AssistantPage {
  protected readonly i18n = inject(I18n);
  private readonly assistant = inject(AssistantService);
  private readonly pois = inject(PoisService);

  protected readonly maxLength = MAX_QUESTION_LENGTH;
  protected readonly question = signal('');
  // A new object per submission, so asking the same question again asks again.
  private readonly submitted = signal<{ text: string } | null>(null);

  protected readonly answer = rxResource({
    params: () => {
      const submitted = this.submitted();
      return submitted ? { question: submitted.text, language: this.i18n.language() } : undefined;
    },
    stream: ({ params }) => this.assistant.ask(params.question, params.language),
  });

  /** Cards of the cited points, fetched by id (D-042). */
  protected readonly cited = rxResource({
    params: () =>
      this.answer.hasValue() && !this.answer.isLoading()
        ? { ids: this.answer.value().ids, language: this.i18n.language() }
        : undefined,
    stream: ({ params }) =>
      params.ids.length === 0
        ? of([])
        : forkJoin(params.ids.map((id) => this.pois.get(id, params.language))),
  });

  /** Loading and error messages take the place of the answer in the announced region. */
  protected readonly statusMessage = computed(() => {
    const texts = this.i18n.texts().assistant;
    if (this.answer.isLoading()) {
      return texts.thinking;
    }
    const error = this.answer.error();
    return error ? (apiErrorDetail(error) ?? texts.unreachable) : null;
  });

  /** A 422 from /preguntar is about the question itself, so it is tied to the text box. */
  protected readonly invalidQuestion = computed(() => {
    const error = this.answer.error();
    return error !== undefined && apiErrorDetail(error) !== null;
  });

  protected readonly answerParts = computed(() =>
    this.answer.hasValue() ? splitAnswer(this.answer.value().respuesta) : null,
  );

  protected type(event: Event): void {
    this.question.set((event.target as HTMLInputElement).value);
  }

  protected submit(event: Event): void {
    event.preventDefault();
    this.submitted.set({ text: this.question() });
  }

  protected ask(question: string): void {
    this.question.set(question);
    this.submitted.set({ text: question });
  }
}
