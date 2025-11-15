// frontend/src/interface/components/client/ClientCreateDrawer.tsx

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../../components/ui/dialog';
import type {
  ClientCreateDto,
  ClientDto,
} from '../../../domain/client/types';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import styles from './client-create-drawer.module.css';

const schema = z.object({
  name: z.string().min(1, 'Le nom est requis'),
  email: z.string().email('Email invalide').optional().or(z.literal('')),
  phone: z.string().optional(),
  address: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface ClientCreateDrawerProps {
  open: boolean;
  onClose: () => void;
  onClientCreated: (client: ClientDto) => void;
}

export default function ClientCreateDrawer({
  open,
  onClose,
  onClientCreated,
}: ClientCreateDrawerProps) {
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
    setError,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = handleSubmit(async (data) => {
    setServerError(null);
    try {
      const payload: ClientCreateDto = {
        name: data.name,
        email: data.email || undefined,
        phone: data.phone || undefined,
        address: data.address || undefined,
      };

      const newClient = await clientRepository.create(payload);
      reset();
      onClientCreated(newClient);
      onClose();
    } catch (err: unknown) {
      // Handle 400 validation error from backend
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as {
          response?: { status?: number; data?: { name?: string } };
        };
        if (axiosErr.response?.status === 400) {
          const nameError = axiosErr.response.data?.name;
          if (nameError) {
            setError('name', { message: nameError });
            return;
          }
        }
      }
      setServerError('Une erreur est survenue lors de la création du client.');
    }
  });

  const handleClose = () => {
    reset();
    setServerError(null);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className={styles.drawerContent}>
        <DialogHeader>
          <DialogTitle>Nouveau client</DialogTitle>
          <DialogDescription>
            Créez un nouveau client pour cette facture.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={onSubmit} className={styles.form} noValidate>
          <div className={styles.formBody}>
            {serverError && (
              <div className={styles.serverError}>{serverError}</div>
            )}

            <div className={styles.field}>
              <label htmlFor="name" className={styles.label}>
                Nom <span className={styles.required}>*</span>
              </label>
              <input
                id="name"
                type="text"
                placeholder="Entreprise SARL"
                {...register('name')}
                className={styles.input}
                aria-invalid={!!errors.name}
                aria-describedby={errors.name ? 'name-error' : undefined}
              />
              {errors.name && (
                <small id="name-error" className={styles.error}>
                  {errors.name.message}
                </small>
              )}
            </div>

            <div className={styles.field}>
              <label htmlFor="email" className={styles.label}>
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="contact@entreprise.com"
                {...register('email')}
                className={styles.input}
                aria-invalid={!!errors.email}
                aria-describedby={errors.email ? 'email-error' : undefined}
              />
              {errors.email && (
                <small id="email-error" className={styles.error}>
                  {errors.email.message}
                </small>
              )}
            </div>

            <div className={styles.field}>
              <label htmlFor="phone" className={styles.label}>
                Téléphone
              </label>
              <input
                id="phone"
                type="tel"
                placeholder="+33 6 12 34 56 78"
                {...register('phone')}
                className={styles.input}
                aria-invalid={!!errors.phone}
                aria-describedby={errors.phone ? 'phone-error' : undefined}
              />
              {errors.phone && (
                <small id="phone-error" className={styles.error}>
                  {errors.phone.message}
                </small>
              )}
            </div>

            <div className={styles.field}>
              <label htmlFor="address" className={styles.label}>
                Adresse
              </label>
              <textarea
                id="address"
                placeholder="123 Rue Example, 75001 Paris"
                {...register('address')}
                className={styles.textarea}
                rows={3}
                aria-invalid={!!errors.address}
                aria-describedby={errors.address ? 'address-error' : undefined}
              />
              {errors.address && (
                <small id="address-error" className={styles.error}>
                  {errors.address.message}
                </small>
              )}
            </div>
          </div>

          <DialogFooter className={styles.footer}>
            <button
              type="button"
              onClick={handleClose}
              className={styles.buttonCancel}
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className={styles.buttonSubmit}
            >
              {isSubmitting ? 'Création...' : 'Créer le client'}
            </button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
