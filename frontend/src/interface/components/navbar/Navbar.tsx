import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Navbar.module.css';
import { useAuth } from '../../../app/providers/AuthProvider';

/**
 * Accepts an unknown value and returns the first found logout-like function
 * (logout | signOut | logoutUser) bound to the provided object.
 */
function getLogoutFn(a: unknown): (() => Promise<void>) | null {
  if (!a || typeof a !== 'object') return null;

  const auth = a as Record<string, unknown>;

  const getFn = (key: string) => auth[key];
  const tryBind = (key: string) => {
    const candidate = getFn(key);
    if (typeof candidate === 'function') {
      // cast to the expected signature without using `any`
      return (candidate as (...args: unknown[]) => Promise<void>).bind(auth);
    }
    return null;
  };

  return tryBind('logout') ?? tryBind('signOut') ?? tryBind('logoutUser');
}

export default function Navbar() {
  const auth = useAuth();
  const user = auth.user;
  const logoutFn = getLogoutFn(auth);

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    try {
      if (logoutFn) {
        await logoutFn();
      } else {
        console.warn('logout function not provided by useAuth()');
      }
    } catch (error) {
      // error is used here so eslint won't complain about an unused variable
      console.error('Logout failed', error);
    }
  };

  return (
    <header
      className={styles.header}
      role="banner"
      aria-label="Barre de navigation FreelanSign"
    >
      <div className={styles.container}>
        <div className={styles.brandWrapper}>
          <Link to="/" className={styles.brand}>
            FreelanSign
          </Link>
        </div>

        <nav className={styles.nav} aria-label="Navigation principale">
          <ul className={styles.navList}>
            {user ? (
              <>
                <li>
                  <Link to="/quotes/create" className={styles.navLink}>
                    Créer un devis
                  </Link>
                </li>
                <li>
                  <button
                    onClick={handleLogout}
                    className={styles.navLink}
                    aria-label="Se déconnecter"
                  >
                    Déconnexion
                  </button>
                </li>
              </>
            ) : (
              <>
                <li>
                  <Link to="/register" className={styles.navLink}>
                    Créer un compte
                  </Link>
                </li>
                <li>
                  <Link to="/login" className={styles.navLink}>
                    Connexion
                  </Link>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
}
