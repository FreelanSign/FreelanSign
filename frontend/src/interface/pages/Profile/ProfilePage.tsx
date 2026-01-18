// src/interface/pages/ProfilePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import { useAuth } from '../../../app/providers/AuthProvider';
import type { AccountDto } from '../../../domain/account/types';
import type { PrestationDto } from '../../../domain/catalog/types';
import type { UserDto } from '../../../domain/user/types';
import { accountRepository } from '../../../infrastructure/account/accountRepository';
import { useAccountStore } from '../../../infrastructure/account/accountStore';
import { catalogRepository } from '../../../infrastructure/catalog/catalogRepository';
import { userRepository } from '../../../infrastructure/user/userRepository';

import { Briefcase, Mail, PencilLine, Phone } from 'lucide-react';
import { useRequireAccount } from '../../hooks/useRequireAccount';

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

  if (loading)
    return <div className="text-center py-8">Chargement du profil…</div>;

  const fullName = user
    ? `${user.profile?.first_name || ''} ${user.profile?.last_name || ''}`.trim() ||
      'Utilisateur'
    : 'Utilisateur';

  return (
    <div className="container mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header Profil */}
      <header className="flex flex-col sm:flex-row items-center gap-6 p-8 bg-white rounded-xl border border-border shadow-sm">
        <div className="relative group">
          <div className="w-20 h-20 rounded-full overflow-hidden border-4 border-muted shadow-inner">
            <img
              src={user?.profile?.avatar_url || '/img/default-avatar.jpeg'}
              alt="Avatar"
              className="object-cover w-full h-full transition-transform duration-300 group-hover:scale-110"
            />
          </div>
        </div>

        <div className="flex-1 text-center sm:text-left space-y-1">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 font-playfair">
            {fullName}
          </h1>
          <div className="flex flex-col sm:flex-row items-center justify-center sm:justify-start gap-x-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <Mail className="h-3.5 w-3.5" />{' '}
              {user?.email || authUser?.email || '—'}
            </span>
            {user?.profile?.phone && (
              <span className="flex items-center gap-1.5">
                <Phone className="h-3.5 w-3.5" /> {user.profile.phone}
              </span>
            )}
          </div>
        </div>

        <Button
          onClick={() => navigate('/profile/edit')}
          className="btn-add-client"
        >
          <PencilLine className="mr-2 h-4 w-4" />
          Modifier
        </Button>
      </header>

      {/* Carte Informations Pro */}
      {account && account !== 'loading' && (
        <Card className="shadow-sm border border-border overflow-hidden">
          <CardHeader className="bg-muted/30 border-b border-border/50 py-4">
            <CardTitle className="text-base flex items-center gap-3">
              <Briefcase className="h-4 w-4 text-brand" />
              {account.display_name || 'Structure professionnelle'}
              {account.legal_form && (
                <Badge variant="tag" className="ml-1">
                  {account.legal_form}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="py-2 px-6">
            <div className="info-row">
              <span className="info-label">Domaine d'activité</span>
              <span className="info-value">{areaName || '—'}</span>
            </div>

            <div className="info-row">
              <span className="info-label">Tarif Journalier (TJM)</span>
              <span className="info-value text-brand">
                {account.default_rate_cents
                  ? `${(account.default_rate_cents / 100).toFixed(2)} €`
                  : '—'}
              </span>
            </div>

            <div className="info-row">
              <span className="info-label">Numéro SIRET</span>
              <span className="info-value tracking-wider font-mono">
                {account.legal_id || '—'}
              </span>
            </div>

            <div className="info-row">
              <span className="info-label">Adresse professionnelle</span>
              <span className="info-value">
                {account.address_line1 || account.city ? (
                  <div className="flex flex-col">
                    {account.address_line1 && (
                      <span>{account.address_line1}</span>
                    )}
                    {account.address_line2 && (
                      <span>{account.address_line2}</span>
                    )}
                    {(account.postal_code || account.city) && (
                      <span>
                        {[account.postal_code, account.city]
                          .filter(Boolean)
                          .join(' ')}
                      </span>
                    )}
                    {account.country && <span>{account.country}</span>}
                  </div>
                ) : (
                  '—'
                )}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Carte Prestations */}
      {account && account !== 'loading' && (
        <Card className="shadow-sm border border-border">
          <CardHeader className="py-4 border-b border-border/30">
            <CardTitle className="text-base">
              Prestations au catalogue
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            {prestations === 'loading' ? (
              <div className="flex items-center gap-2 text-muted-foreground italic text-sm">
                <span className="animate-pulse">
                  Chargement des services...
                </span>
              </div>
            ) : prestations && prestations.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {prestations.map((p) => (
                  <Badge
                    key={p.id}
                    variant="outline"
                    className="bg-brand/5 text-brand border-brand/20 px-3 py-1 font-medium"
                  >
                    {p.name || p.title || p.label || 'Service'}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground italic">
                Aucune prestation configurée pour ce profil.
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
