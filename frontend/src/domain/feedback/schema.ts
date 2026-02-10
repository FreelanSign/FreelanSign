// domain/feedback/schema.ts
import { z } from 'zod';

export const feedbackSchema = z.object({
  category: z.enum(['BUG', 'SUGGESTION', 'QUESTION', 'KUDOS'], {
    error: 'Veuillez choisir une categorie',
  }),
  message: z
    .string()
    .min(10, 'Le message doit contenir au moins 10 caracteres')
    .max(2000, 'Le message ne doit pas depasser 2000 caracteres'),
});

export type FeedbackFormData = z.infer<typeof feedbackSchema>;
