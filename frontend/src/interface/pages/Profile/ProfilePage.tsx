// src/interface/pages/ProfilePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { AccountDto } from '../../../domain/account/types';
import type { PrestationDto } from '../../../domain/catalog/types';
import type { UserDto } from '../../../domain/user/types';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';

import { useRequireAccount } from '../../hooks/useRequireAccount';
import styles from './profile-page.module.css';

/**
 * Page profil: affiche user.profile + professional (si présent)
 * et liste détaillée des prestations liées au professional.
 */

export default function ProfilePage() {
  const { user: authUser } = useAuth();
  const activeAccountId = useAccountStore((state) => state.activeAccountId);
  const [user, setUser] = useState<UserDto | null>(null);
  const [account, setAccount] = useState<AccountDto | null | 'loading'>(
    'loading',
  );
  const [prestations, setPrestations] = useState<
    PrestationDto[] | 'loading' | null
  >(null);
  const [areaName, setAreaName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useRequireAccount({ loading });

  // helper type-guard
  function isApiError(e: unknown): e is { response?: { status?: number } } {
    return (
      typeof e === 'object' &&
      e !== null &&
      'response' in e &&
      typeof (e as Record<string, unknown>).response === 'object'
    );
  }

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const me = await userRepository.getMe();
        if (!mounted) return;
        setUser(me);

        if (activeAccountId) {
          const acc = await accountRepository.retrieve(activeAccountId);
          if (!mounted) return;
          setAccount(acc ?? null);

          if (acc) {
            setPrestations('loading');

            const ids = acc.service_type_ids ?? [];
            try {
              const prestationsResult =
                await catalogRepository.getPrestationsByIds(ids);
              if (!mounted) return;
              setPrestations(prestationsResult);
            } catch (err) {
              console.error('Erreur récupération prestations', err);
              if (!mounted) return;
              setPrestations(null);
            }

            try {
              const area = await catalogRepository.getAreaById(acc.domain_id);
              if (!mounted) return;
              setAreaName(area?.name ?? null);
            } catch (err) {
              console.warn('Erreur récupération domaine', err);
              if (!mounted) return;
              setAreaName(null);
            }
          }
        } else {
          setAccount(null);
        }
      } catch (e: unknown) {
        if (isApiError(e) && e.response?.status === 401) {
          navigate('/login', { replace: true });
        } else {
          console.error('ProfilePage load error', e);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [navigate, activeAccountId]);

  if (loading) return <div>Chargement du profil…</div>;

  const fullName = user
    ? `${user.profile?.first_name || ''} ${user.profile?.last_name || ''}`.trim() ||
      'Utilisateur'
    : 'Utilisateur';

  return (
    <div className="grid gap-6">
      {/* Compact User Header */}
      <header className={styles.header}>
        <div className={styles.avatarWrap}>
          <img
            src={user?.profile?.avatar_url || '/img/default-avatar.jpeg'}
            alt="Avatar"
            className={styles.avatarImg}
          />
        </div>
        <div className={styles.headerContent}>
          <h1 className={styles.userName}>{fullName}</h1>
          <div className={styles.meta}>
            <span className={styles.metaItem}>
              {user?.email || authUser?.email || '—'}
            </span>
            {user?.profile?.phone && (
              <span className={styles.metaItem}>{user.profile.phone}</span>
            )}
          </div>
        </div>
        <button
          onClick={() => navigate('/profile/edit')}
          className={`${styles.buttonPrimary} ${styles.editButton}`}
        >
          Modifier
        </button>
      </header>

      {/* Professional Info Card */}
      {account && account !== 'loading' && (
        <section className={styles.card}>
          <h2 className={styles.h2}>
            {account.display_name || 'Structure professionnelle'}
            {account.legal_form && (
              <span className={`${styles.badge} ${styles.badgeInfo}`}>
                {account.legal_form}
              </span>
            )}
          </h2>

          <div className={styles.kv}>
            <span>Domaine</span>
            <strong>{areaName || '—'}</strong>
          </div>

          <div className={styles.kv}>
            <span>TJM</span>
            <strong>
              {account.default_rate_cents
                ? `${(account.default_rate_cents / 100).toFixed(2)} €`
                : '—'}
            </strong>
          </div>

          <div className={styles.kv}>
            <span>SIRET</span>
            <strong>{account.legal_id || '—'}</strong>
          </div>
        </section>
      )}

      {/* Services Card */}
      {account && account !== 'loading' && (
        <section className={styles.card}>
          <h2 className={styles.h2}>Prestations</h2>
          {prestations === 'loading' ? (
            <p className={styles.emptyServices}>Chargement des prestations…</p>
          ) : prestations && prestations.length > 0 ? (
            <div className={styles.servicesGrid}>
              {prestations.map((p) => (
                <span key={p.id} className={styles.chip}>
                  {p.name || p.title || p.label || 'Service'}
                </span>
              ))}
            </div>
          ) : (
            <p className={styles.emptyServices}>Aucune prestation configurée</p>
          )}
        </section>
      )}
    </div>
  );
}
