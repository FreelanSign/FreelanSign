// pages/branding/ThemeEditPage.tsx
import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import ThemeForm, {
  type ThemeFormData,
} from '../../components/branding/ThemesForm';
import { normalizeSpacing, normalizeTypography } from '../../utils/branding';
import styles from './themes.module.css';

export default function ThemeEditPage() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(false);
  const [loadingTheme, setLoadingTheme] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [initialData, setInitialData] = useState<ThemeFormData | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadTheme() {
      if (!id) {
        setError('ID du thème manquant');
        setLoadingTheme(false);
        return;
      }

      try {
        setLoadingTheme(true);
        const theme = await themeRepository.get(id);

        setInitialData({
          name: theme.name,
          isActive: theme.is_active,
          colors: theme.colors,
          typography: normalizeTypography(theme.typography),
          spacing: normalizeSpacing(theme.spacing),
          logo: null, // On ne charge pas le fichier existant
        });
      } catch (err: unknown) {
        const error = err as { message?: string };
        setError(error.message || 'Erreur lors du chargement du thème');
      } finally {
        setLoadingTheme(false);
      }
    }

    loadTheme();
  }, [id]);

  async function handleSubmit(data: ThemeFormData) {
    if (!id) {
      setError('ID du thème manquant');
      return;
    }

    if (!data.name.trim()) {
      setError('Le nom du thème est requis');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await themeRepository.update(id, {
        name: data.name,
        is_active: data.isActive,
        colors: data.colors,
        typography: normalizeTypography(data.typography),
        spacing: normalizeSpacing(data.spacing),
        ...(data.logo ? { logo: data.logo } : {}),
      });
      navigate('/branding/themes');
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'Erreur lors de la mise à jour du thème');
    } finally {
      setLoading(false);
    }
  }

  if (loadingTheme) {
    return (
      <div className="grid gap-6">
        <div className={styles.headerRow}>
          <div>
            <h1 className={styles.title}>Chargement...</h1>
          </div>
        </div>
        <div className={styles.card}>
          <div className={styles.skel}></div>
          <div className={styles.skel} style={{ marginTop: '1rem' }}></div>
          <div className={styles.skel} style={{ marginTop: '1rem' }}></div>
        </div>
      </div>
    );
  }

  if (error && !initialData) {
    return (
      <div className="grid gap-6">
        <div className={styles.headerRow}>
          <div>
            <h1 className={styles.title}>Erreur</h1>
          </div>
          <Link
            to="/branding/themes"
            className={`${styles.btn} ${styles.btnGhost}`}
          >
            ← Retour
          </Link>
        </div>
        <div className={styles.error}>{error}</div>
      </div>
    );
  }

  if (!initialData) {
    return null;
  }

  return (
    <div className="grid gap-6">
      <div className={styles.headerRow}>
        <div>
          <h1 className={styles.title}>Modifier le thème</h1>
          <p className={styles.headerSubtitle}>
            Ajustez les paramètres de votre thème
          </p>
        </div>
        <Link
          to="/branding/themes"
          className={`${styles.btn} ${styles.btnGhost}`}
        >
          ← Retour
        </Link>
      </div>

      <ThemeForm
        initialData={initialData}
        onSubmit={handleSubmit}
        submitLabel="💾  Enregistrer les modifications"
        isLoading={loading}
        error={error}
      />
    </div>
  );
}
