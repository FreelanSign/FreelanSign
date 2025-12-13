// frontend/src/interface/components/client/ClientCreateDrawer.tsx

import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../../components/ui/dialog';
import type { ClientCreateDto, ClientDto } from '../../../domain/client/types';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import ClientFormFields from './ClientFormFields';
import {
  clientValidationSchema,
  type ClientFormData,
} from './clientFormSchema';
import styles from './client-create-drawer.module.css';

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
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientValidationSchema),
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
        <DialogHeader className={styles.header}>
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

            <ClientFormFields register={register} errors={errors} />
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
