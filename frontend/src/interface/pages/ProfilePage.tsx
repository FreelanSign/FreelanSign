// src/interface/pages/ProfilePage.tsx
import React, { useEffect, useState } from 'react';
import { userRepository } from '../../infrastructure/user/userRepository';
import { catalogRepository } from '../../infrastructure/catalog/catalogRepository';
import type { UserDto, ProfessionalUserDto } from '../../domain/user/types';
import type { PrestationDto } from '../../domain/catalog/types';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';

/**
 * Page profil: affiche user.profile + professional (si présent)
 * et liste détaillée des prestations liées au professional.
 */

export default function ProfilePage() {
  const { user: authUser } = useAuth();
  const [user, setUser] = useState<UserDto | null>(null);
  const [professional, setProfessional] = useState<ProfessionalUserDto | null | 'loading'>('loading');
  const [prestations, setPrestations] = useState<PrestationDto[] | 'loading' | null>(null);
  const [areaName, setAreaName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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

        // Si professional présent -> fetch services & domaine
        if (prof) {
          // Init state to loading
          setPrestations('loading');

          // fetch prestations (ids)
          const ids = prof.service_types ?? [];
          try {
            const prestationsResult = await catalogRepository.getPrestationsByIds(ids);
            if (!mounted) return;
            setPrestations(prestationsResult);
          } catch (err) {
            console.error('Erreur récupération prestations', err);
            if (!mounted) return;
            setPrestations(null); // signifie échec / non disponible
          }

          // fetch domaine (Area) si présent
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
      } catch (e) {
        if ((e as any)?.response?.status === 401) {
          navigate('/login', { replace: true });
        } else {
          console.error('ProfilePage load error', e);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, [navigate]);

  if (loading) return <main className="container p-6">Chargement du profil…</main>;

  return (
    <main className="container mx-auto p-6 grid gap-6">
      <h1 className="text-2xl font-semibold">Mon profil</h1>

      <section className="p-4 border rounded">
        <h2 className="font-medium">Utilisateur</h2>
        <p><strong>Email :</strong> {user?.email ?? authUser?.email}</p>
        <p>
          <strong>Nom :</strong>{' '}
          {user?.profile?.first_name || user?.profile?.last_name
            ? `${user?.profile?.first_name ?? ''} ${user?.profile?.last_name ?? ''}`.trim()
            : '—'}
        </p>
        <p><strong>Téléphone :</strong> {user?.profile?.phone ?? '—'}</p>
        {user?.profile?.avatar_url && (
          <img src={user.profile.avatar_url} alt="avatar" className="w-24 h-24 rounded-full mt-2" />
        )}
      </section>

      <section className="p-4 border rounded">
        <h2 className="font-medium">Compte professionnel</h2>
        {professional === 'loading' ? (
          <p>Chargement…</p>
        ) : professional ? (
          <>
            <p><strong>Nom structure :</strong> {professional.name ?? '—'}</p>
            <p><strong>Statut juridique :</strong> {professional.status_juridique ?? '—'}</p>
            <p><strong>Domaine :</strong> {areaName ?? '—'}</p>
            <p><strong>TJM :</strong> {professional.tjm_cents ? (professional.tjm_cents / 100).toFixed(2) + ' €' : '—'}</p>
            <p><strong>Numéro pro :</strong> {professional.number_pro ?? '—'}</p>
            <p><strong>Crée le :</strong> {professional.created_at ?? '—'}</p>

            <div className="mt-4">
              <h3 className="font-medium">Services proposés</h3>

              {/* plusieurs états possibles : loading | null (erreur/none) | array */}
              {prestations === 'loading' ? (
                <p>Chargement des services…</p>
              ) : prestations === null ? (
                <p>Impossible de charger les services pour le moment.</p>
              ) : prestations.length === 0 ? (
                <p>Aucun service renseigné.</p>
              ) : (
                <ul className="grid gap-3">
                  {prestations.map((p) => (
                    <li key={p.id} className="p-3 border rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <strong className="block text-lg">
                            {p.name ?? p.title ?? p.label ?? `Service #${p.id}`}
                          </strong>
                          { (p.short_description ?? p.description) && (
                            <p className="text-sm mt-1">{p.short_description ?? p.description}</p>
                          )}
                        </div>
                        <div className="text-right">
                          {p.price_cents != null ? (
                            <div className="text-sm font-medium">{(p.price_cents / 100).toFixed(2)} €</div>
                          ) : null}
                        </div>
                      </div>

                      {/* link vers page de détail (si tu en as une) */}
                      {/* <div className="mt-2">
                        <Link to={`/services/${p.id}`} className="text-blue-600 underline">Voir le service</Link>
                      </div> */}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        ) : (
          <p>Vous n'avez pas encore de profil professionnel. <button onClick={() => navigate('/onboarding-professional')} className="underline">Commencer l'onboarding</button></p>
        )}
      </section>
    </main>
  );
}
