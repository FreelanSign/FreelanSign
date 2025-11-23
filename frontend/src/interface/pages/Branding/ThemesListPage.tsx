
// src/interface/pages/Branding/ThemesListPage.tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { ThemeListItem } from '../../../infrastructure/branding/themeRepository';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import { useThemes } from '../../hooks/useThemes';
import styles from './themes.module.css';


/** Helpers type-safe pour récupérer un message d'erreur sans any */
function isErrorWithMessage(e: unknown): e is { message: string } {
  return (
    typeof e === 'object' &&
    e !== null &&
    'message' in e &&
    typeof (e as Record<string, unknown>).message === 'string'
  );
}
function getErrorMessage(
  e: unknown,
  fallback = 'Une erreur est survenue',
): string {
  if (isErrorWithMessage(e)) return e.message;
  if (typeof e === 'string') return e;
  return fallback;
}

export default function ThemesListPage() {
  const { themes, loading, error } = useThemes();

  // état local pour pouvoir refléter l’activation sans recharger
  const [list, setList] = useState<ThemeListItem[]>([]);
  const [activatingId, setActivatingId] = useState<string | number | null>(
    null,
  );
  const [actError, setActError] = useState<string | null>(null);
  const [deactivatingId, setDeactivatingId] = useState<string | number | null>(
    null,
  );
  const [, setDeactError] = useState<string | null>(null); // on élide la valeur pour éviter TS6133

  useEffect(() => {
    setList(themes);
  }, [themes]);

  async function handleActivate(id: string | number) {
    try {
      setActError(null);
      setActivatingId(id);
      const activated = await themeRepository.activate(String(id));
      // MAJ locale : un seul thème actif
      setList((prev) =>
        prev.map((t) => ({
          ...t,
          is_active: String(t.id) === String(activated.id),
        })),
      );
    } catch (e: unknown) {
      console.error(e);
      setActError(getErrorMessage(e, 'Activation impossible'));
    } finally {
      setActivatingId(null);
    }
  }

  async function handleDeactivate(id: string | number) {
    try {
      setDeactError(null);
      setDeactivatingId(id);
      const deactivated = await themeRepository.deactivate(String(id));
      // MAJ locale : ne change que l’item ciblé selon la valeur renvoyée par l’API
      setList((prev) =>
        prev.map((t) =>
          String(t.id) === String(deactivated.id)
            ? { ...t, is_active: deactivated.is_active }
            : t,
        ),
      );
    } catch (e: unknown) {
      console.error(e);
      setDeactError(getErrorMessage(e, 'Désactivation impossible'));
    } finally {
      setDeactivatingId(null);
    }
  }

  const Shell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="grid gap-6">
      {children}
    </div>
  );

  return (
    <Shell>
      <div className={styles.headerRow}>
        <div>
          <h1 className={styles.title}>Mes Templates de devis</h1>
          <p className={styles.headerSubtitle}>
            Active un template pour l’utiliser dans tes PDFs.
          </p>
        </div>
        <div className={styles.actions}>
          <Link
            to="/branding/themes/new/"
            className={`${styles.btn} ${styles.btnPrimary}`}
          >
            + Nouveau Template
          </Link>
          <Link to="/dashboard" className={`${styles.btn} ${styles.btnGhost}`}>
            ← Dashboard
          </Link>
        </div>
      </div>

      {loading ? (
        <div className={styles.card}>
          <div className={styles.skel} />
          <div className={styles.skel} />
        </div>
      ) : error ? (
        <div className={styles.error}>
          Erreur : {error.message ?? 'Erreur inconnue'}
        </div>
      ) : list.length === 0 ? (
        <div className={styles.empty}>
          Aucun Template pour le moment. Crée ton premier Template pour
          personnaliser tes PDF.
        </div>
      ) : (
        <div className={styles.card}>
          {actError && (
            <div className={styles.error}>Activation : {actError}</div>
          )}

          <ul className={styles.list}>
            {list.map((t) => (
              <li key={t.id} className={styles.item}>
                <div className={styles.itemLeft}>
                  <div className={styles.itemTitle}>{t.name}</div>
                  <div className={styles.itemMeta}>
                    Modifié le{' '}
                    {new Intl.DateTimeFormat(undefined, {
                      year: 'numeric',
                      month: 'short',
                      day: '2-digit',
                    }).format(new Date(t.updated_at))}
                  </div>
                  {t.is_active ? (
                    <span className={styles.badgeActive}>Actif</span>
                  ) : (
                    <span className={styles.badge}>Inactif</span>
                  )}
                </div>

                <div className={styles.itemActions}>
                  <Link
                    to={`/branding/themes/${t.id}/edit`}
                    className={`${styles.btn} ${styles.btnOutline} ${styles.btnSm}`}
                  >
                    Modifier
                  </Link>

                  {t.is_active ? (
                    <button
                      className={`${styles.btn} ${styles.btnDangerSoft} ${styles.btnSm}`}
                      onClick={() => handleDeactivate(t.id)}
                      disabled={deactivatingId === t.id}
                      aria-busy={deactivatingId === t.id}
                    >
                      {deactivatingId === t.id ? (
                        <>
                          <span className={styles.spinner} /> Désactivation…
                        </>
                      ) : (
                        'Désactiver'
                      )}
                    </button>
                  ) : (
                    <button
                      className={`${styles.btn} ${styles.btnSuccess} ${styles.btnSm}`}
                      onClick={() => handleActivate(t.id)}
                      disabled={activatingId === t.id}
                      aria-busy={activatingId === t.id}
                    >
                      {activatingId === t.id ? (
                        <>
                          <span className={styles.spinner} /> Activation…
                        </>
                      ) : (
                        'Activer'
                      )}
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </Shell>
  );
}
