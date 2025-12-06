import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styles from './sidebar.module.css';

const IconWrapper: React.FC<{
  active?: boolean;
  children: React.ReactNode;
}> = ({ active, children }) => {
  return (
    <div className={`${styles.icon} ${active ? styles.active : ''}`}>
      {children}
    </div>
  );
};

const handleNotAvailable = (e: React.MouseEvent) => {
  e.preventDefault();
  alert('Disponible prochainement');
};

const Sidebar: React.FC = () => {
  const location = useLocation();
  const items = [
    {
      to: '/quotes/new',
      label: 'Nouveau',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M12 5v14M5 12h14"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      to: '/dashboard',
      label: 'Accueil',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M3 11.5L12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1V11.5z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
    {
      to: '/branding/themes',
      label: 'Thèmes',
      icon: (
        <img
          src="/src/assets/icons/pen-nib-line.svg"
          width={20}
          height={20}
          alt="Thèmes"
        />
      ),
    },
    {
      to: '/legal-terms',
      label: 'CGV',
      icon: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
          <path
            d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M14 2v6h6M16 13H8M16 17H8M10 9H8"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ),
    },
  ];

  return (
    <aside className={styles.sidebar} aria-label="Menu principal">
      <div className={styles.avatarWrap}>
        <img
          src={'/img/default-avatar.jpeg'}
          alt="Avatar"
          className={styles.avatarImg}
        />
      </div>

      <nav className={styles.nav} aria-label="Navigation principale">
        {items.map((it) => {
          const active = location.pathname === it.to;
          return (
            <Link key={it.to} to={it.to} title={it.label} aria-label={it.label}>
              <IconWrapper active={active}>{it.icon}</IconWrapper>
            </Link>
          );
        })}
      </nav>

      <div className={styles.bottom}>
        <Link
          to="/settings"
          title="Paramètres"
          onClick={handleNotAvailable}
          aria-label="Paramètres"
        >
          <div className={styles.icon}>
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
            >
              <path
                d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09c.7 0 1.27-.37 1.51-1a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06c.5.5 1.2.66 1.82.33.48-.26 1.1-.19 1.51-.19H9a2 2 0 0 1 4 0h.09c.4 0 1.03-.07 1.51.19.62.33 1.32.17 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06c-.5.5-.66 1.2-.33 1.82.26.48.19 1.1.19 1.51V9a2 2 0 0 1 0 4h-.09c-.7 0-1.27.37-1.51 1z"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </Link>
      </div>
    </aside>
  );
};

export default Sidebar;
