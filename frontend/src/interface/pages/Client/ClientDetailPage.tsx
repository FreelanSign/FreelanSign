import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import type { ClientDto } from '../../../domain/client/types';
import { clientRepository } from '../../../infrastructure/client/clientRepository';
import { quoteRepository } from '../../../infrastructure/quote/quoteRepository';
import DeleteConfirmDialog from '../../components/common/DeleteConfirmDialog';
import styles from './client-detail.module.css';

type QuoteItem = {
  id: string;
  reference: string;
  title: string;
  status: string;
  issue_date?: string | null;
  total?: number | string | null;
  currency?: string | null;
};

function StatusBadge({ status }: { status: string }) {
  const s = (status ?? '').toLowerCase();
  const map: Record<string, string> = {
    draft: styles.badge,
    sent: `${styles.badge} ${styles.badgeInfo}`,
    accepted: `${styles.badge} ${styles.badgeSuccess}`,
    paid: `${styles.badge} ${styles.badgeSuccess}`,
    expired: `${styles.badge} ${styles.badgeWarning}`,
    refused: `${styles.badge} ${styles.badgeDanger}`,
    rejected: `${styles.badge} ${styles.badgeDanger}`,
    cancelled: styles.badge,
    canceled: styles.badge,
  };
  return <span className={map[s] ?? styles.badge}>{status}</span>;
}

export default function ClientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [client, setClient] = useState<ClientDto | null>(null);
  const [quotes, setQuotes] = useState<QuoteItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const [clientData, quotesData] = await Promise.all([
          clientRepository.retrieve(id),
          quoteRepository.list({ client: id, page_size: 100 }),
        ]);
        if (!active) return;
        setClient(clientData);
        setQuotes(quotesData.results as QuoteItem[]);
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
  }, [id]);

  const handleDelete = async () => {
    if (!id) return;

    setDeleting(true);
    setDeleteError(null);
    try {
      await clientRepository.delete(id);
      navigate('/clients');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const detail = error.response?.data?.detail;
      if (detail && detail.includes('devis actifs')) {
        setDeleteError(
          "Impossible de supprimer ce client car il a des devis actifs. Veuillez d'abord supprimer ou archiver ses devis.",
        );
      } else {
        setDeleteError('Erreur lors de la suppression du client.');
      }
    } finally {
      setDeleting(false);
    }
  };

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
        <div className={styles.skel + ' ' + styles.skelCard} />
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell>
        <div className={styles.error}>Erreur : {error}</div>
        <Link to="/clients" className={styles.btn + ' ' + styles.btnGhost}>
          ← Retour à la liste
        </Link>
      </Shell>
    );
  }

  if (!client) {
    return (
      <Shell>
        <div>Aucun client à afficher.</div>
        <Link to="/clients" className={styles.btn + ' ' + styles.btnGhost}>
          ← Retour à la liste
        </Link>
      </Shell>
    );
  }

  return (
    <Shell>
      <header className={styles.header}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className={styles.title}>{client.name}</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link to="/clients" className={`${styles.btn} ${styles.btnGhost}`}>
              ← Retour
            </Link>
            <Link
              to={`/clients/${client.id}/edit`}
              className={`${styles.btn} ${styles.btnPrimary}`}
            >
              Éditer
            </Link>
            <button
              onClick={() => setDeleteDialogOpen(true)}
              className={`${styles.btn} ${styles.btnDanger}`}
            >
              Supprimer
            </button>
          </div>
        </div>
      </header>

      {/* Client Info */}
      <section className={styles.card}>
        <h2 className={styles.h2}>Informations client</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <div className={styles.kv}>
              <span>Nom</span>
              <strong>{client.name}</strong>
            </div>
            <div className={styles.kv}>
              <span>Email</span>
              <strong>{client.email || '—'}</strong>
            </div>
            <div className={styles.kv}>
              <span>Téléphone</span>
              <strong>{client.phone || '—'}</strong>
            </div>
          </div>
          <div>
            <div className={styles.kv}>
              <span>Adresse</span>
              <strong>
                {[
                  client.company,
                  client.address_line1,
                  client.address_line2,
                  [client.postal_code, client.city].filter(Boolean).join(' '),
                  client.country,
                ]
                  .filter(Boolean)
                  .join(', ') || '—'}
              </strong>
            </div>
          </div>
        </div>
      </section>

      {/* Quotes History */}
      <section className={styles.card}>
        <h2 className={styles.h2}>Historique des devis ({quotes.length})</h2>
        {quotes.length === 0 ? (
          <div className={styles.empty}>
            Aucun devis pour ce client.
            <br />
            <Link
              to="/quotes/new"
              className={`${styles.btn} ${styles.btnPrimary}`}
              style={{ marginTop: '12px' }}
            >
              Créer un devis
            </Link>
          </div>
        ) : (
          <div className={styles.quotesTable}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Titre</th>
                  <th>Statut</th>
                  <th>Date</th>
                  <th>Total</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {quotes.map((quote) => (
                  <tr key={quote.id}>
                    <td className={styles.refCell}>{quote.reference}</td>
                    <td>{quote.title}</td>
                    <td>
                      <StatusBadge status={quote.status} />
                    </td>
                    <td>
                      {quote.issue_date
                        ? new Intl.DateTimeFormat(undefined, {
                            year: 'numeric',
                            month: 'short',
                            day: '2-digit',
                          }).format(new Date(quote.issue_date))
                        : '—'}
                    </td>
                    <td>
                      {quote.total != null
                        ? `${Number(quote.total).toFixed(2)} ${quote.currency ?? '€'}`
                        : '—'}
                    </td>
                    <td>
                      <Link to={`/quotes/${quote.id}`} className={styles.link}>
                        Voir
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setDeleteError(null);
        }}
        onConfirm={handleDelete}
        title="Supprimer le client"
        message={`Êtes-vous sûr de vouloir supprimer le client "${client.name}" ? Cette action est irréversible.`}
        isDeleting={deleting}
        errorMessage={deleteError}
      />
    </Shell>
  );
}
