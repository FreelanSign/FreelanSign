// src/interface/pages/ProfilePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../app/providers/AuthProvider';
import type { PrestationDto } from '../../../domain/catalog/types';
import type { ProfessionalUserDto, UserDto } from '../../../domain/user/types';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';

import Sidebar from '../../components/sidebar/Sidebar';
import Navbar from '../../components/navbar/Navbar';
import styles from './profile-page.module.css';

/**
 * Page profil: affiche user.profile + professional (si présent)
 * et liste détaillée des prestations liées au professional.
 */

export default function ProfilePage() {
  const { user: authUser } = useAuth();
  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<
    ProfessionalUserDto | null | 'loading'
  >('loading');
  const [prestations, setPrestations] = useState<
    PrestationDto[] | 'loading' | null
  >(null);
  const [areaName, setAreaName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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

        const prof = await userRepository.getProfessionalMe();
        if (!mounted) return;
        setProfessional(prof ?? null);

        if (prof) {
          setPrestations('loading');

          const ids = prof.service_type_ids ?? [];
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
            const domaineId = prof.domaine as unknown as number | null;
            const area = await catalogRepository.getAreaById(domaineId);
            if (!mounted) return;
            setAreaName(area?.name ?? null);
          } catch (err) {
            console.warn('Erreur récupération domaine', err);
            if (!mounted) return;
            setAreaName(null);
          }
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
  }, [navigate]);

  if (loading)
    return (
      <>
        <Sidebar />
        <div className={styles.page}>
          <Navbar />
          <main className={styles.inner}>Chargement du profil…</main>
        </div>
      </>
    );

  const fullName = user
    ? `${user.profile?.first_name || ''} ${user.profile?.last_name || ''}`.trim() ||
      'Utilisateur'
    : 'Utilisateur';

  return (
    <>
      <Sidebar />
      <div className={styles.page}>
        <Navbar />
        <main className={`${styles.inner} container mx-auto grid gap-6`}>
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
          {professional && professional !== 'loading' && (
            <section className={styles.card}>
              <h2 className={styles.h2}>
                {professional.name || 'Structure professionnelle'}
                {professional.status_juridique && (
                  <span className={`${styles.badge} ${styles.badgeInfo}`}>
                    {professional.status_juridique}
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
                  {professional.tjm_cents
                    ? `${(professional.tjm_cents / 100).toFixed(2)} €`
                    : '—'}
                </strong>
              </div>

              <div className={styles.kv}>
                <span>SIRET</span>
                <strong>{professional.number_pro || '—'}</strong>
              </div>
            </section>
          )}

          {/* Services Card */}
          {professional && professional !== 'loading' && (
            <section className={styles.card}>
              <h2 className={styles.h2}>Prestations</h2>
              {prestations === 'loading' ? (
                <p className={styles.emptyServices}>
                  Chargement des prestations…
                </p>
              ) : prestations && prestations.length > 0 ? (
                <div className={styles.servicesGrid}>
                  {prestations.map((p) => (
                    <span key={p.id} className={styles.chip}>
                      {p.name || p.title || p.label || 'Service'}
                    </span>
                  ))}
                </div>
              ) : (
                <p className={styles.emptyServices}>
                  Aucune prestation configurée
                </p>
              )}
            </section>
          )}
        </main>
      </div>
    </>
  );
}
