import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useParams } from 'react-router-dom';
import type { ClientDto } from '../../../domain/client/types';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import ClientFormFields from '../../components/client/ClientFormFields';
import {
  clientValidationSchema,
  type ClientFormData,
} from '../../components/client/clientFormSchema';
import styles from './client-edit.module.css';

export default function ClientEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [client, setClient] = useState<ClientDto | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setError: setFieldError,
  } = useForm<ClientFormData>({
    resolver: zodResolver(clientValidationSchema),
  });

  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await clientRepository.retrieve(id);
        if (!active) return;
        setClient(data);
        reset({
          name: data.name,
          email: data.email || '',
          phone: data.phone || '',
          address: data.address || '',
        });
      } catch (err: unknown) {
        if (!active) return;
        const e = err as { response?: { data?: unknown }; message?: string };
        const server = e.response?.data;
        setError(server ? JSON.stringify(server) : (e.message ?? 'Erreur'));
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [id, reset]);

  const onSubmit = handleSubmit(async (data) => {
    if (!id) return;

    setSaving(true);
    setError(null);
    try {
      const payload = {
        name: data.name,
        email: data.email || undefined,
        phone: data.phone || undefined,
        address: data.address || undefined,
      };

      await clientRepository.update(id, payload);
      navigate(`/clients/${id}`);
    } catch (err: unknown) {
      // Handle 400 validation error from backend
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as {
          response?: { status?: number; data?: { name?: string } };
        };
        if (axiosErr.response?.status === 400) {
          const nameError = axiosErr.response.data?.name;
          if (nameError) {
            setFieldError('name', { message: nameError });
            return;
          }
        }
      }
      setError('Erreur lors de la mise à jour du client.');
    } finally {
      setSaving(false);
    }
  });

  const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className={styles.page}>
      <div className={styles.inner}>{children}</div>
    </div>
  );

  if (loading) {
    return (
      <Shell>
        <div className={styles.skel + ' ' + styles.skelHeader} />
        <div className={styles.skel + ' ' + styles.skelCard} />
      </Shell>
    );
  }

  if (error && !client) {
    return (
      <Shell>
        <div className={styles.error}>Erreur : {error}</div>
        <Link
          to={id ? `/clients/${id}` : '/clients'}
          className={`${styles.btn} ${styles.btnGhost}`}
        >
          ← Retour
        </Link>
      </Shell>
    );
  }

  if (!client) {
    return (
      <Shell>
        <div>Client introuvable.</div>
        <Link to="/clients" className={`${styles.btn} ${styles.btnGhost}`}>
          ← Retour à la liste
        </Link>
      </Shell>
    );
  }

  return (
    <Shell>
      <header className={styles.header}>
        <h1 className={styles.title}>Éditer le client</h1>
        <div className={styles.actions}>
          <Link
            to={`/clients/${id}`}
            className={`${styles.btn} ${styles.btnGhost}`}
          >
            Annuler
          </Link>
          <button
            onClick={onSubmit}
            disabled={saving}
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            {saving ? 'Enregistrement...' : 'Enregistrer'}
          </button>
        </div>
      </header>

      <form onSubmit={onSubmit} className={styles.card}>
        {error && <div className={styles.serverError}>{error}</div>}

        <div className={styles.formGrid}>
          <ClientFormFields register={register} errors={errors} />
        </div>
      </form>
    </Shell>
  );
}
