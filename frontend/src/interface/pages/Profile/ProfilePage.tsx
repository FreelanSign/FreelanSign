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
      {/* Compact User Header */}
      <header className="flex flex-col sm:flex-row items-center gap-4 p-6 bg-white rounded-lg border border-border shadow-sm">
        <div className="relative w-16 h-16 rounded-full overflow-hidden border-2 border-border">
          <img
            src={user?.profile?.avatar_url || '/img/default-avatar.jpeg'}
            alt="Avatar"
            className="object-cover w-full h-full"
          />
        </div>
        <div className="flex-1 text-center sm:text-left">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 font-playfair">
            {fullName}
          </h1>
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 text-sm text-muted-foreground mt-1">
            <span>{user?.email || authUser?.email || '—'}</span>
            {user?.profile?.phone && <span>{user.profile.phone}</span>}
          </div>
        </div>
        <Button
          onClick={() => navigate('/profile/edit')}
          className="bg-brand text-brand-foreground hover:bg-brand/90"
        >
          Modifier
        </Button>
      </header>

      {/* Professional Info Card */}
      {account && account !== 'loading' && (
        <Card className="shadow-sm border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {account.display_name || 'Structure professionnelle'}
              {account.legal_form && (
                <Badge variant="secondary">{account.legal_form}</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Domaine</span>
              <strong className="text-sm">{areaName || '—'}</strong>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">TJM</span>
              <strong className="text-sm">
                {account.default_rate_cents
                  ? `${(account.default_rate_cents / 100).toFixed(2)} €`
                  : '—'}
              </strong>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">SIRET</span>
              <strong className="text-sm">{account.legal_id || '—'}</strong>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Services Card */}
      {account && account !== 'loading' && (
        <Card className="shadow-sm border border-border">
          <CardHeader>
            <CardTitle>Prestations</CardTitle>
          </CardHeader>
          <CardContent>
            {prestations === 'loading' ? (
              <p className="text-muted-foreground">
                Chargement des prestations…
              </p>
            ) : prestations && prestations.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {prestations.map((p) => (
                  <Badge
                    key={p.id}
                    variant="outline"
                    className="bg-brand/10 text-brand border-brand/20"
                  >
                    {p.name || p.title || p.label || 'Service'}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">
                Aucune prestation configurée
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
