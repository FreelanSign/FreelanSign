// domain/feedback/types.ts
export type FeedbackCategory = 'BUG' | 'SUGGESTION' | 'QUESTION' | 'KUDOS';

export type CreateFeedbackPayload = {
  category: FeedbackCategory;
  message: string;
};
