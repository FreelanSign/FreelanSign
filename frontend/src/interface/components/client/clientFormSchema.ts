// frontend/src/interface/components/client/clientFormSchema.ts

import { z } from 'zod';

export const clientValidationSchema = z.object({
  name: z.string().min(1, 'Le nom est requis'),
  email: z.string().email('Email invalide').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
  // Structured address fields
  address_line1: z.string().optional(),
  address_line2: z.string().optional(),
  city: z.string().optional(),
  postal_code: z.string().optional(),
  country: z.string().max(2, 'Code pays ISO (2 caractères)').optional(),
  company: z.string().optional(),
});

export type ClientFormData = z.infer<typeof clientValidationSchema>;
