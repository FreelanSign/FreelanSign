import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { ClientDto } from '../../../domain/client/types';
import {
  clientRepository,
  type PageResponse,
} from '../../../infrastructure/client/clientRepository';
import ClientCreateDrawer from '../../components/client/ClientCreateDrawer';
import DeleteConfirmDialog from '../../components/common/DeleteConfirmDialog';
import styles from './clients-list.module.css';

type ColumnPrefs = {
  email: boolean;
  phone: boolean;
  address: boolean;
};

const DEFAULT_COLUMNS: ColumnPrefs = {
  email: true,
  phone: true,
  address: false,
};

const STORAGE_KEY = 'freelansign_client_columns_v1';

export default function ClientsListPage() {
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(20);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PageResponse<ClientDto> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  const [columnPrefs, setColumnPrefs] = useState<ColumnPrefs>(DEFAULT_COLUMNS);

  const [drawerOpen, setDrawerOpen] = useState(false);

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<ClientDto | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Load column preferences from localStorage
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setColumnPrefs(JSON.parse(stored));
      } catch {
        setColumnPrefs(DEFAULT_COLUMNS);
      }
    }
  }, []);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1); // Reset to page 1 on search
    }, 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch clients
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await clientRepository.list({
          search: debouncedSearch || undefined,
          page,
          page_size: pageSize,
        });
        if (!active) return;
        setData(res);
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
  }, [page, pageSize, debouncedSearch]);

  const next = data?.next ? () => setPage((p) => p + 1) : undefined;
  const prev = data?.previous
    ? () => setPage((p) => Math.max(1, p - 1))
    : undefined;

  const toggleColumn = (col: keyof ColumnPrefs) => {
    const updated = { ...columnPrefs, [col]: !columnPrefs[col] };
    setColumnPrefs(updated);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  };

  const handleClientCreated = async () => {
    // Refresh list
    try {
      const res = await clientRepository.list({
        search: debouncedSearch || undefined,
        page,
        page_size: pageSize,
      });
      setData(res);
    } catch {
      // Ignore error, list will refresh on next load
    }
  };

  const openDeleteDialog = (client: ClientDto) => {
    setClientToDelete(client);
    setDeleteDialogOpen(true);
    setDeleteError(null);
  };

  const handleDelete = async () => {
    if (!clientToDelete) return;

    setDeleting(true);
    setDeleteError(null);
    try {
      await clientRepository.delete(clientToDelete.id);
      setDeleteDialogOpen(false);
      setClientToDelete(null);
      // Refresh list
      const res = await clientRepository.list({
        search: debouncedSearch || undefined,
        page,
        page_size: pageSize,
      });
      setData(res);
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
        <div className={styles.card}>
          <div className={styles.skel + ' ' + styles.skelItem} />
          <div className={styles.skel + ' ' + styles.skelItem} />
          <div className={styles.skel + ' ' + styles.skelItem} />
        </div>
      </Shell>
    );
  }

  if (error) {
    return (
      <Shell>
        <div className={styles.headerRow}>
          <h1 className={styles.title}>Mes clients</h1>
        </div>
        <div className={styles.error}>Erreur : {error}</div>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className={styles.headerRow}>
        <h1 className={styles.title}>Mes clients</h1>
        <div className={styles.actions}>
          <button
            onClick={() => setDrawerOpen(true)}
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            + Nouveau client
          </button>
        </div>
      </div>

      {/* Search & Column Selector */}
      <div className={styles.controls}>
        <input
          type="search"
          placeholder="Rechercher par nom ou email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
        <div className={styles.columnSelector}>
          <span className={styles.columnLabel}>Colonnes :</span>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={true}
              disabled={true}
              style={{ cursor: 'not-allowed' }}
            />
            Nom (obligatoire)
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={columnPrefs.email}
              onChange={() => toggleColumn('email')}
            />
            Email
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={columnPrefs.phone}
              onChange={() => toggleColumn('phone')}
            />
            Téléphone
          </label>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={columnPrefs.address}
              onChange={() => toggleColumn('address')}
            />
            Adresse
          </label>
        </div>
      </div>

      {!data || (Array.isArray(data.results) && data.results.length === 0) ? (
        <div className={styles.empty}>
          Aucun client trouvé.
          {!searchTerm && (
            <>
              <br />
              <button
                onClick={() => setDrawerOpen(true)}
                className={`${styles.btn} ${styles.btnPrimary}`}
                style={{ marginTop: '12px' }}
              >
                Créer mon premier client
              </button>
            </>
          )}
        </div>
      ) : (
        <div className={styles.card}>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Nom</th>
                  {columnPrefs.email && <th>Email</th>}
                  {columnPrefs.phone && <th>Téléphone</th>}
                  {columnPrefs.address && <th>Adresse</th>}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((client) => (
                  <tr key={client.id}>
                    <td className={styles.nameCell}>{client.name}</td>
                    {columnPrefs.email && <td>{client.email || '—'}</td>}
                    {columnPrefs.phone && <td>{client.phone || '—'}</td>}
                    {columnPrefs.address && <td>{client.address || '—'}</td>}
                    <td className={styles.actionsCell}>
                      <Link
                        to={`/clients/${client.id}`}
                        className={styles.link}
                      >
                        Voir
                      </Link>
                      <Link
                        to={`/clients/${client.id}/edit`}
                        className={styles.link}
                      >
                        Éditer
                      </Link>
                      <button
                        onClick={() => openDeleteDialog(client)}
                        className={styles.linkButton}
                      >
                        Supprimer
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className={styles.pagination}>
            <div>
              Page {page} — {data?.count ?? '—'} clients
            </div>
            <div className="flex gap-2">
              <button
                onClick={prev}
                disabled={!prev}
                className={styles.pagerBtn}
              >
                Précédent
              </button>
              <button
                onClick={next}
                disabled={!next}
                className={styles.pagerBtn}
              >
                Suivant
              </button>
            </div>
          </div>
        </div>
      )}

      <ClientCreateDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onClientCreated={handleClientCreated}
      />

      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onClose={() => {
          setDeleteDialogOpen(false);
          setClientToDelete(null);
          setDeleteError(null);
        }}
        onConfirm={handleDelete}
        title="Supprimer le client"
        message={`Êtes-vous sûr de vouloir supprimer le client "${clientToDelete?.name}" ? Cette action est irréversible.`}
        isDeleting={deleting}
        errorMessage={deleteError}
      />
    </Shell>
  );
}
