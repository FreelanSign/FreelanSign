import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { LegalTermsPreviewDto } from '../../../domain/legal-terms/types';
import { legalTermsRepository } from '../../../infrastructure/legal-terms/legalTermsRepository';
import { useRequireAccount } from '../../hooks/useRequireAccount';
import styles from './legal-terms-page.module.css';

export default function LegalTermsPage() {
  const [preview, setPreview] = useState<LegalTermsPreviewDto | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useRequireAccount({ loading });

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const data = await legalTermsRepository.getPreview();
        if (!mounted) return;
        setPreview(data);
      } catch (err: unknown) {
        console.error('Error loading legal terms preview', err);
        if (!mounted) return;

        const errorMsg =
          err && typeof err === 'object' && 'response' in err
            ? 'Données légales manquantes (SIRET, téléphone, etc.). Complétez votre profil.'
            : 'Erreur lors du chargement des conditions générales.';
        setError(errorMsg);
      } finally {
        if (mounted) setLoading(false);
      }
    })();

    return () => {
      mounted = false;
    };
  }, []);

  if (loading) return <div>Chargement des conditions générales…</div>;

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className={styles.errorCard}>
          <h2 className={styles.errorTitle}>Erreur</h2>
          <p className={styles.errorText}>{error}</p>
          <button
            onClick={() => navigate('/profile/edit')}
            className={styles.buttonPrimary}
          >
            Compléter mon profil
          </button>
        </div>
      </div>
    );
  }

  if (!preview) return <div>Aucune condition générale disponible.</div>;

  return (
    <div className="grid gap-6">
      <header className={styles.header}>
        <h1 className={styles.title}>Conditions Générales de Vente</h1>
        <span className={styles.version}>
          Version {preview.template_version}
        </span>
      </header>

      <section className={styles.infoBanner}>
        <div className={styles.infoBannerIcon}>✓</div>
        <div>
          <p className={styles.infoBannerText}>
            Ces conditions sont automatiquement attachées à tous vos devis.
          </p>
          <p className={styles.infoBannerSubtext}>
            Les variables (SIRET, adresse, etc.) sont substituées
            automatiquement.
          </p>
        </div>
      </section>

      <section className={styles.card}>
        <h2 className={styles.h2}>Clauses ({preview.clauses.length})</h2>
        <div className={styles.clausesList}>
          {preview.clauses.map((clause) => (
            <div key={clause.identifier} className={styles.clauseCard}>
              <div className={styles.clauseHeader}>
                <h3 className={styles.clauseTitle}>{clause.title}</h3>
                <div className={styles.badgeGroup}>
                  {clause.is_mandatory && (
                    <span
                      className={`${styles.badge} ${styles.badgeMandatory}`}
                    >
                      Obligatoire
                    </span>
                  )}
                  {clause.was_customized && (
                    <span
                      className={`${styles.badge} ${styles.badgeCustomized}`}
                    >
                      Personnalisée
                    </span>
                  )}
                </div>
              </div>
              <div
                className={styles.clauseBody}
                dangerouslySetInnerHTML={{ __html: clause.body }}
              />
            </div>
          ))}
        </div>
      </section>

      <section className={styles.card}>
        <h2 className={styles.h2}>Aperçu complet</h2>
        <div
          className={styles.preview}
          dangerouslySetInnerHTML={{ __html: preview.rendered_html }}
        />
      </section>
    </div>
  );
}
