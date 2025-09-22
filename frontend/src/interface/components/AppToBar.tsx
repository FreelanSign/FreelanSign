import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../app/providers/AuthProvider';

/** Barre simple affichée sur toutes les pages. */
export default function AppTopBar() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  return (
    <header className="w-full border-b bg-white">
      <div className="container mx-auto p-3 flex items-center justify-between gap-3">
        <Link to="/dashboard" className="font-semibold">
          FreelanSign
        </Link>

        <nav className="flex items-center gap-2">
          {/* Affiche le bouton partout sauf sur la page de création */}
          {pathname !== '/quotes/new' && user && (
            <Link
              to="/quotes/new"
              className="rounded px-3 py-2 bg-green-600 text-white"
              title="Créer un devis"
            >
              + Créer un devis
            </Link>
          )}
          {user ? (
            <>
              <Link to="/profile" className="rounded px-3 py-2 bg-gray-100">
                Mon profil
              </Link>
              <button
                onClick={() => logout()}
                className="rounded px-3 py-2 bg-gray-200"
              >
                Déconnexion
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded px-3 py-2 bg-blue-600 text-white"
            >
              Se connecter
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
