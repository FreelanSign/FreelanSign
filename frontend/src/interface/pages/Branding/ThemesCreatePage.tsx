// pages/branding/ThemeCreatePage.tsx
import { Button } from '@/components/ui/button';
import { ArrowLeft, Palette, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { themeRepository } from '../../../infrastructure/branding/themeRepository';
import ThemeForm, {
  type ThemeFormData,
} from '../../components/branding/ThemesForm';

const DEFAULT_COLORS = {
  primary: '#00C896',
  secondary: '#00C896',
  background: '#ffffff', // Locked: always white for professional docs
  text_primary: '#222222', // Locked: always near-black for readability
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
    <div className="container mx-auto max-w-7xl py-8 space-y-10 animate-in fade-in duration-700">
      {/* Header Section */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-2 border-b border-gray-100">
        <div className="space-y-2">
          <div className="flex items-center gap-3 text-muted-foreground mb-1">
            <Button
              variant="ghost"
              size="icon"
              asChild
              className="h-8 w-8 -ml-2 rounded-full"
            >
              <Link to="/branding/themes">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <span className="text-xs font-bold uppercase tracking-widest">
              Configuration visuelle
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-gray-900 font-playfair flex items-center gap-3">
            Créer un nouveau thème
            <Sparkles className="h-6 w-6 text-brand/40" />
          </h1>
          <p className="text-muted-foreground text-sm flex items-center gap-2">
            <Palette className="h-4 w-4 text-brand" />
            Définissez l'identité unique de vos documents professionnels
          </p>
        </div>
      </section>

      <ThemeForm
        initialData={initialData}
        onSubmit={handleSubmit}
        submitLabel="Créer le template"
        isLoading={loading}
        error={error}
      />
    </div>
  );
}
