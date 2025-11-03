// components/branding/ThemeForm.tsx
import { type FormEvent, useState } from 'react';
import { ChromePicker, type ColorResult } from 'react-color';
import styles from '../../pages/branding/themes.module.css';

const COLOR_LABELS: Record<string, string> = {
  primary: 'Primaire',
  secondary: 'Secondaire',
  background: 'Arrière-plan',
  text_primary: 'Texte principal',
  text_secondary: 'Texte secondaire',
  border: 'Bordure',
  highlight: 'Accentuation',
};

export type ThemeFormData = {
  name: string;
  isActive: boolean;
  colors: Record<string, string>;
  typography: {
    heading_font: string;
    body_font: string;
    font_sizes: {
      h1: number;
      h2: number;
      h3: number;
      body: number;
      small: number;
    };
    line_heights: {
      heading: number;
      body: number;
    };
  };
  spacing: {
    page_margin: number;
    section_spacing: number;
    element_padding: number;
  };
  logo?: File | null;
};

type ThemeFormProps = {
  initialData: ThemeFormData;
  onSubmit: (data: ThemeFormData) => Promise<void>;
  submitLabel: string;
  isLoading: boolean;
  error: string | null;
};

export default function ThemeForm({
  initialData,
  onSubmit,
  submitLabel,
  isLoading,
  error,
}: ThemeFormProps) {
  const [name, setName] = useState(initialData.name);
  const [isActive, setIsActive] = useState(initialData.isActive);
  const [colors, setColors] = useState(initialData.colors);
  const [typography, setTypography] = useState(initialData.typography);
  const [spacing, setSpacing] = useState(initialData.spacing);
  const [logo] = useState<File | null>(initialData.logo || null);
  const [openPicker, setOpenPicker] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await onSubmit({
      name: name.trim(),
      isActive,
      colors,
      typography,
      spacing,
      logo,
    });
  }

  return (
    <form onSubmit={handleSubmit} className={styles.formContainer}>
      {error && (
        <div className={styles.error}>
          <strong>Erreur :</strong> {error}
        </div>
      )}

      {/* Section Informations générales */}
      <div className={styles.formSection}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderContent}>
            <h2 className={styles.sectionTitle}>📋 Informations générales</h2>
            <p className={styles.sectionDesc}>
              Configurez les paramètres de base de votre thème
            </p>
          </div>
        </div>
        <div className={styles.sectionContent}>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>
              Nom du thème <span className={styles.required}>*</span>
            </label>
            <input
              className={styles.input}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Thème Corporate, Thème Moderne..."
              required
            />
            <span className={styles.help}>
              Choisissez un nom descriptif pour votre thème
            </span>
          </div>

          <div className={styles.checkboxGroup}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                className={styles.checkbox}
              />
              <span>
                <strong>Activer ce thème immédiatement</strong>
                <small className={styles.checkboxHint}>
                  Le thème sera disponible dès sa sauvegarde
                </small>
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Section Couleurs */}
      <div className={styles.formSection}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderContent}>
            <h2 className={styles.sectionTitle}>🎨 Palette de couleurs</h2>
            <p className={styles.sectionDesc}>
              Définissez les couleurs principales de votre identité visuelle
            </p>
          </div>
        </div>
        <div className={styles.sectionContent}>
          <div className={styles.colorsGrid}>
            {Object.entries(colors).map(([key, val]) => (
              <div key={key} className={styles.colorField}>
                <label className={styles.label}>
                  {COLOR_LABELS[key] || key}
                </label>
                <div className={styles.colorRow}>
                  <div className={styles.colorPickerWrapper}>
                    <button
                      type="button"
                      className={styles.colorPickerButton}
                      onClick={() =>
                        setOpenPicker(openPicker === key ? null : key)
                      }
                      style={{ backgroundColor: val }}
                      title="Ouvrir le sélecteur de couleur"
                    >
                      <span className={styles.colorPickerIcon}>🎨</span>
                    </button>
                    {openPicker === key && (
                      <>
                        <div
                          className={styles.colorPickerCover}
                          onClick={() => setOpenPicker(null)}
                        />
                        <div className={styles.colorPickerPopover}>
                          <ChromePicker
                            color={val}
                            onChange={(color: ColorResult) => {
                              setColors((prev) => ({
                                ...prev,
                                [key]: color.hex,
                              }));
                            }}
                            disableAlpha
                          />
                        </div>
                      </>
                    )}
                  </div>
                  <input
                    className={styles.input}
                    value={val}
                    onChange={(e) =>
                      setColors((prev) => ({ ...prev, [key]: e.target.value }))
                    }
                    placeholder="#000000"
                    pattern="^#[0-9A-Fa-f]{6}$"
                  />
                  <span
                    className={styles.colorPreview}
                    style={{ backgroundColor: val }}
                    title={val}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Section Typographie */}
      <div className={styles.formSection}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderContent}>
            <h2 className={styles.sectionTitle}>✍️ Typographie</h2>
            <p className={styles.sectionDesc}>
              Configurez les polices et la hiérarchie de texte
            </p>
          </div>
        </div>
        <div className={styles.sectionContent}>
          {/* Polices - Section désactivée */}
          <div className={styles.subSection}>
            <div
              className={styles.disabledSection}
              data-tooltip="La personnalisation des polices arrive bientôt 👀"
            >
              <h3 className={styles.subSectionTitle}>
                Polices de caractères
                <span className={styles.badgeSoon}>bientôt</span>
              </h3>
              <p className={styles.disabledHint}>
                💡 Pour l'instant, nous utilisons la typographie Inter par
                défaut de FreelanSign.
              </p>
              <div className={styles.grid2}>
                <div className={styles.fieldGroup}>
                  <label className={styles.label}>Police des titres</label>
                  <input
                    className={styles.input}
                    value={typography.heading_font}
                    disabled
                    placeholder="Inter"
                  />
                </div>
                <div className={styles.fieldGroup}>
                  <label className={styles.label}>Police du texte</label>
                  <input
                    className={styles.input}
                    value={typography.body_font}
                    disabled
                    placeholder="Inter"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Tailles de police */}
          <div className={styles.subSection}>
            <h3 className={styles.subSectionTitle}>Tailles de police</h3>
            <p className={styles.help} style={{ marginBottom: '1rem' }}>
              Définissez la taille en pixels pour chaque niveau de texte
            </p>
            <div className={styles.grid5}>
              {(['h1', 'h2', 'h3', 'body', 'small'] as const).map((size) => (
                <div key={size} className={styles.fieldGroup}>
                  <label className={styles.label}>{size.toUpperCase()}</label>
                  <div className={styles.inputWithUnit}>
                    <input
                      type="number"
                      min={8}
                      max={72}
                      className={styles.input}
                      value={typography.font_sizes[size]}
                      onChange={(e) =>
                        setTypography((prev) => ({
                          ...prev,
                          font_sizes: {
                            ...prev.font_sizes,
                            [size]: Number(e.target.value),
                          },
                        }))
                      }
                    />
                    <span className={styles.inputUnit}>px</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hauteur de ligne */}
          <div className={styles.subSection}>
            <h3 className={styles.subSectionTitle}>Hauteur de ligne</h3>
            <p className={styles.help} style={{ marginBottom: '1rem' }}>
              Ajustez l'espacement vertical entre les lignes de texte
            </p>
            <div className={styles.grid2}>
              <div className={styles.fieldGroup}>
                <label className={styles.label}>Texte courant</label>
                <input
                  type="number"
                  min={1}
                  max={2.5}
                  step={0.1}
                  className={styles.input}
                  value={typography.line_heights.body}
                  onChange={(e) =>
                    setTypography((prev) => ({
                      ...prev,
                      line_heights: {
                        ...prev.line_heights,
                        body: Number(e.target.value),
                      },
                    }))
                  }
                />
              </div>
              <div className={styles.fieldGroup}>
                <label className={styles.label}>Titres</label>
                <input
                  type="number"
                  min={1}
                  max={2.5}
                  step={0.1}
                  className={styles.input}
                  value={typography.line_heights.heading}
                  onChange={(e) =>
                    setTypography((prev) => ({
                      ...prev,
                      line_heights: {
                        ...prev.line_heights,
                        heading: Number(e.target.value),
                      },
                    }))
                  }
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section Espacement */}
      <div className={styles.formSection}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionHeaderContent}>
            <h2 className={styles.sectionTitle}>📐 Espacement</h2>
            <p className={styles.sectionDesc}>
              Contrôlez les marges et espacements de vos documents
            </p>
          </div>
        </div>
        <div className={styles.sectionContent}>
          <div className={styles.grid3}>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Marge de page</label>
              <div className={styles.inputWithUnit}>
                <input
                  type="number"
                  min={0}
                  max={100}
                  className={styles.input}
                  value={spacing.page_margin}
                  onChange={(e) =>
                    setSpacing((prev) => ({
                      ...prev,
                      page_margin: Number(e.target.value),
                    }))
                  }
                />
                <span className={styles.inputUnit}>px</span>
              </div>
              <span className={styles.help}>Espace autour du contenu</span>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Espacement sections</label>
              <div className={styles.inputWithUnit}>
                <input
                  type="number"
                  min={0}
                  max={100}
                  className={styles.input}
                  value={spacing.section_spacing}
                  onChange={(e) =>
                    setSpacing((prev) => ({
                      ...prev,
                      section_spacing: Number(e.target.value),
                    }))
                  }
                />
                <span className={styles.inputUnit}>px</span>
              </div>
              <span className={styles.help}>Entre les sections</span>
            </div>
            <div className={styles.fieldGroup}>
              <label className={styles.label}>Padding éléments</label>
              <div className={styles.inputWithUnit}>
                <input
                  type="number"
                  min={0}
                  max={100}
                  className={styles.input}
                  value={spacing.element_padding}
                  onChange={(e) =>
                    setSpacing((prev) => ({
                      ...prev,
                      element_padding: Number(e.target.value),
                    }))
                  }
                />
                <span className={styles.inputUnit}>px</span>
              </div>
              <span className={styles.help}>À l'intérieur des blocs</span>
            </div>
          </div>
        </div>
      </div>

      {/* Boutons d'action */}
      <div className={styles.formActions}>
        <button
          type="submit"
          className={`${styles.btn} ${styles.btnPrimary}`}
          disabled={isLoading || !name.trim()}
        >
          {isLoading ? (
            <>
              <span className={styles.spinner}></span>
              Enregistrement...
            </>
          ) : (
            submitLabel
          )}
        </button>
      </div>
    </form>
  );
}
