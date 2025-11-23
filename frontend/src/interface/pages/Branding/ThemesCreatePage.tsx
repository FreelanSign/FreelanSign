
// pages/branding/ThemeCreatePage.tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import ThemeForm, {
  type ThemeFormData,
} from '../../components/branding/ThemesForm';
import styles from './themes.module.css';

const DEFAULT_COLORS = {
  primary: '#2456c2',
  secondary: '#3ccf91',
  background: '#f5f7fa',
  text_primary: '#222222',
  text_secondary: '#666666',
  border: '#e5e7eb',
  highlight: '#ff8a3d',
};

const DEFAULT_TYPO = {
  heading_font: 'Inter',
  body_font: 'Inter',
  font_sizes: {
    h1: 20,
    h2: 16,
    h3: 13,
    body: 12,
    small: 10,
  },
  line_heights: {
    heading: 1.2,
    body: 1.5,
  },
};

const DEFAULT_SPACING = {
  page_margin: 40,
  section_spacing: 12,
  element_padding: 8,
};

export default function ThemeCreatePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const initialData: ThemeFormData = {
    name: '',
    isActive: true,
    colors: { ...DEFAULT_COLORS },
    typography: { ...DEFAULT_TYPO },
    spacing: { ...DEFAULT_SPACING },
    logo: null,
  };

  async function handleSubmit(data: ThemeFormData) {
    if (!data.name.trim()) {
      setError('Le nom du thème est requis');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await themeRepository.create({
        name: data.name,
        is_active: data.isActive,
        colors: data.colors,
        typography: data.typography,
        spacing: data.spacing,
        ...(data.logo ? { logo: data.logo } : {}),
      });
      navigate('/branding/themes');
    } catch (err: unknown) {
      const error = err as { message?: string };
      setError(error.message || 'Erreur lors de la création du thème');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6">
      <div className={styles.headerRow}>
        <div>
          <h1 className={styles.title}>Créer un nouveau thème</h1>
          <p className={styles.headerSubtitle}>
            Personnalisez l'apparence de vos documents avec un thème sur mesure
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
        submitLabel="✨ Créer le thème"
        isLoading={loading}
        error={error}
      />
    </div>
  );
}
