import React from 'react';
import { Link } from 'react-router-dom';
import pkg from '../../../../package.json';
import styles from './footer.module.css';

export default function Footer() {
  const currentYear = new Date().getFullYear();
  const version = pkg.version;

  const handleNotAvailable = (e: React.MouseEvent) => {
    e.preventDefault();
    alert('Disponible prochainement');
  };

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.column}>
          <h3 className={styles.title}>Freelansign</h3>
          <p className={styles.text}>
            La solution de gestion simplifiée pour les freelances.
          </p>
        </div>

        <div className={styles.column}>
          <h3 className={styles.title}>Liens utiles</h3>
          <a href="#" onClick={handleNotAvailable} className={styles.link}>
            Support
          </a>
          <Link to="/cgu" className={styles.link}>
            CGU
          </Link>
          <Link to="/confidentialite" className={styles.link}>
            Confidentialité
          </Link>
        </div>

        <div className={styles.column}>
          <h3 className={styles.title}>Informations</h3>
          <Link
            to="/changelog"
            onClick={handleNotAvailable}
            className={styles.link}
          >
            Version {version}
          </Link>
          <div className={styles.status}>
            <span className={styles.dot}></span>
            Système opérationnel
          </div>
        </div>

        <div className={styles.column}>
          <h3 className={styles.title}>Contact</h3>
          <a href="mailto:freelansign@gmail.com" className={styles.link}>
            freelansign@gmail.com
          </a>
        </div>
      </div>

      <div className={styles.copyright}>
        <p className={styles.text}>
          &copy; {currentYear} Freelansign. Tous droits réservés.
        </p>
        <p className={styles.text}>
          Conçu avec passion par{' '}
          <a
            href="https://bertrandrenaudin.fr"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.link}
          >
            Bertrand Renaudin
          </a>
        </p>
      </div>
    </footer>
  );
}
