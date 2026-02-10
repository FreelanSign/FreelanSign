// infrastructure/feedback/feedbackRepository.ts
import { apiClient } from '../http/apiClient';
import type { CreateFeedbackPayload } from '../../domain/feedback/types';

export const feedbackRepository = {
  async create(payload: CreateFeedbackPayload): Promise<void> {
    await apiClient.post('/api/feedback/', payload);
  },
};
