// src/interface/components/branding/ThemesForm.tsx
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import {
  AlertCircle,
  Eye,
  Info,
  Layout,
  Lock,
  MousePointer2,
  Palette,
  Save,
  Settings,
  Sparkles,
  Type,
} from 'lucide-react';
import { type FormEvent, useState } from 'react';
import { ChromePicker, type ColorResult } from 'react-color';

// Define which colors are editable and which are locked
const LOCKED_COLORS = ['background', 'text_primary'];

const COLOR_LABELS: Record<string, string> = {
  primary: 'Couleur primaire',
  secondary: 'Couleur secondaire',
  background: 'Arrière-plan',
  text_primary: 'Texte principal',
  text_secondary: 'Texte secondaire',
  border: 'Bordure',
  highlight: 'Accentuation',
};

const COLOR_HINTS: Record<string, string> = {
  primary: 'Couleur de votre marque (en-tête, boutons)',
  secondary: 'Couleur secondaire (dégradés, accents)',
  background: 'Fond du document (verrouillé blanc)',
  text_primary: 'Couleur du texte principal (verrouillé noir)',
  text_secondary: 'Texte secondaire (sous-titres, notes)',
  border: 'Couleur des lignes et séparations',
  highlight: 'Points importants (totaux, alertes)',
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
  const [typography] = useState(initialData.typography);
  const [spacing, setSpacing] = useState(initialData.spacing);
  const [logo] = useState<File | null>(initialData.logo || null);

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

  const isColorLocked = (key: string) => LOCKED_COLORS.includes(key);

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700"
    >
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive text-sm p-4 rounded-xl flex items-center gap-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <div className="flex flex-col">
            <span className="font-bold">Une erreur est survenue</span>
            <span className="opacity-90">{error}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Main Configuration Area */}
        <div className="lg:col-span-8 space-y-8">
          <Tabs defaultValue="basics" className="w-full space-y-6">
            <div className="bg-white p-1 rounded-2xl border border-gray-100 shadow-sm inline-flex">
              <TabsList className="bg-transparent h-auto p-0 gap-1">
                <TabsTrigger
                  value="basics"
                  className="rounded-xl px-6 py-2.5 data-[state=active]:bg-brand data-[state=active]:text-white transition-all font-bold text-xs uppercase tracking-widest"
                >
                  Général
                </TabsTrigger>
                <TabsTrigger
                  value="colors"
                  className="rounded-xl px-6 py-2.5 data-[state=active]:bg-brand data-[state=active]:text-white transition-all font-bold text-xs uppercase tracking-widest"
                >
                  Couleurs
                </TabsTrigger>
                <TabsTrigger
                  value="design"
                  className="rounded-xl px-6 py-2.5 data-[state=active]:bg-brand data-[state=active]:text-white transition-all font-bold text-xs uppercase tracking-widest"
                >
                  Mise en page
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent
              value="basics"
              className="mt-0 focus-visible:outline-none focus-visible:ring-0"
            >
              <Card className="rounded-3xl border-gray-100 shadow-sm overflow-hidden">
                <CardHeader className="bg-gray-50/50 border-b border-gray-100 px-8 py-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                      <Settings className="h-5 w-5 text-gray-500" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-bold">
                        Informations de base
                      </CardTitle>
                      <CardDescription>
                        Identifiez et gérez l'activation de votre thème
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-8 space-y-8">
                  <div className="grid gap-3">
                    <Label
                      htmlFor="theme-name"
                      className="text-sm font-bold uppercase tracking-wider text-gray-400"
                    >
                      Nom du template{' '}
                      <span className="text-destructive">*</span>
                    </Label>
                    <Input
                      id="theme-name"
                      className="h-12 rounded-xl border-gray-100 bg-gray-50 focus-visible:ring-brand focus-visible:border-brand transition-all text-base font-medium"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Ex: Facture Premium, Template Minimaliste..."
                      required
                    />
                    <p className="text-xs text-muted-foreground italic flex items-center gap-1.5">
                      <Info className="h-3 w-3" />
                      Ce nom vous aide à identifier vos différents styles dans
                      la liste.
                    </p>
                  </div>

                  <div
                    className="flex items-start space-x-4 p-5 rounded-2xl bg-brand/5 border border-brand/10 transition-all hover:bg-brand/10 group cursor-pointer"
                    onClick={() => setIsActive(!isActive)}
                  >
                    <div className="pt-1">
                      <Checkbox
                        id="is-active"
                        checked={isActive}
                        onCheckedChange={(checked) => setIsActive(!!checked)}
                        className="rounded-md border-brand/30 data-[state=checked]:bg-brand data-[state=checked]:border-brand h-5 w-5"
                      />
                    </div>
                    <div className="grid gap-1.5 leading-none cursor-pointer">
                      <label
                        htmlFor="is-active"
                        className="text-sm font-bold leading-none cursor-pointer group-hover:text-brand transition-colors"
                      >
                        Appliquer immédiatement
                      </label>
                      <p className="text-xs text-muted-foreground">
                        Si activé, ce thème sera utilisé par défaut pour tous
                        vos devis en cours et à venir.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent
              value="colors"
              className="mt-0 focus-visible:outline-none focus-visible:ring-0"
            >
              <Card className="rounded-3xl border-gray-100 shadow-sm overflow-hidden">
                <CardHeader className="bg-gray-50/50 border-b border-gray-100 px-8 py-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                        <Palette className="h-5 w-5 text-gray-500" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-bold">
                          Palette chromatique
                        </CardTitle>
                        <CardDescription>
                          Configurez les couleurs emblématiques de votre marque
                        </CardDescription>
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className="bg-white border-gray-200 text-gray-400 font-bold uppercase tracking-tighter text-[9px] h-6"
                    >
                      5 couleurs modifiables
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="p-8">
                  <TooltipProvider delayDuration={200}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
                      {Object.entries(colors).map(([key, val]) => {
                        const locked = isColorLocked(key);
                        return (
                          <div
                            key={key}
                            className={`space-y-3 ${locked ? 'opacity-60' : ''}`}
                          >
                            <div className="flex items-center gap-2">
                              <Label className="text-[10px] font-bold uppercase tracking-widest text-gray-400">
                                {COLOR_LABELS[key] || key}
                              </Label>
                              {locked && (
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Lock className="h-3 w-3 text-gray-400" />
                                  </TooltipTrigger>
                                  <TooltipContent
                                    side="top"
                                    className="text-xs max-w-48"
                                  >
                                    Verrouillé pour garantir un aspect
                                    professionnel de vos documents
                                  </TooltipContent>
                                </Tooltip>
                              )}
                            </div>
                            <p className="text-[10px] text-muted-foreground -mt-2">
                              {COLOR_HINTS[key]}
                            </p>
                            <div className="flex items-center gap-2">
                              {locked ? (
                                <div
                                  className="h-10 w-10 shrink-0 rounded-xl border border-gray-200 shadow-sm flex items-center justify-center cursor-not-allowed"
                                  style={{ backgroundColor: val }}
                                >
                                  <Lock className="h-3 w-3 text-gray-400" />
                                </div>
                              ) : (
                                <Popover>
                                  <PopoverTrigger asChild>
                                    <button
                                      type="button"
                                      className="h-10 w-10 shrink-0 rounded-xl border border-gray-100 shadow-sm transition-transform active:scale-95 flex items-center justify-center group relative overflow-hidden"
                                      style={{ backgroundColor: val }}
                                    >
                                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 flex items-center justify-center transition-colors">
                                        <MousePointer2 className="h-4 w-4 text-white opacity-0 group-hover:opacity-100 drop-shadow-md" />
                                      </div>
                                    </button>
                                  </PopoverTrigger>
                                  <PopoverContent
                                    className="p-0 border-none shadow-2xl rounded-2xl overflow-hidden animate-in fade-in zoom-in-95"
                                    side="right"
                                  >
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
                                  </PopoverContent>
                                </Popover>
                              )}
                              <div className="relative flex-1">
                                <Input
                                  className="h-10 rounded-xl border-gray-100 bg-gray-50/50 font-mono text-sm px-4 focus-visible:ring-brand disabled:opacity-50 disabled:cursor-not-allowed"
                                  value={val}
                                  onChange={(e) =>
                                    setColors((prev) => ({
                                      ...prev,
                                      [key]: e.target.value,
                                    }))
                                  }
                                  placeholder="#000000"
                                  pattern="^#[0-9A-Fa-f]{6}$"
                                  disabled={locked}
                                />
                                <div
                                  className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 rounded-full border border-gray-200 shadow-inner pointer-events-none"
                                  style={{ backgroundColor: val }}
                                />
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </TooltipProvider>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent
              value="design"
              className="mt-0 focus-visible:outline-none focus-visible:ring-0 space-y-8"
            >
              {/* Spacing Card */}
              <Card className="rounded-3xl border-gray-100 shadow-sm overflow-hidden">
                <CardHeader className="bg-gray-50/50 border-b border-gray-100 px-8 py-6">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                      <Layout className="h-5 w-5 text-gray-500" />
                    </div>
                    <div>
                      <CardTitle className="text-xl font-bold">
                        Espacement & Marges
                      </CardTitle>
                      <CardDescription>
                        Contrôlez l'équilibre visuel et l'aération des documents
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-8">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="space-y-3">
                      <Label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 italic">
                        Marge de page
                      </Label>
                      <div className="relative">
                        <Input
                          type="number"
                          className="h-10 rounded-xl border-gray-100 bg-gray-50/50 pr-10"
                          value={spacing.page_margin}
                          onChange={(e) =>
                            setSpacing((prev) => ({
                              ...prev,
                              page_margin: Number(e.target.value),
                            }))
                          }
                        />
                        <span className="absolute right-3 top-2.5 text-[10px] font-bold text-gray-400">
                          PX
                        </span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 italic">
                        Sections
                      </Label>
                      <div className="relative">
                        <Input
                          type="number"
                          className="h-10 rounded-xl border-gray-100 bg-gray-50/50 pr-10"
                          value={spacing.section_spacing}
                          onChange={(e) =>
                            setSpacing((prev) => ({
                              ...prev,
                              section_spacing: Number(e.target.value),
                            }))
                          }
                        />
                        <span className="absolute right-3 top-2.5 text-[10px] font-bold text-gray-400">
                          PX
                        </span>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <Label className="text-[10px] font-bold uppercase tracking-widest text-gray-400 italic">
                        Contenu
                      </Label>
                      <div className="relative">
                        <Input
                          type="number"
                          className="h-10 rounded-xl border-gray-100 bg-gray-50/50 pr-10"
                          value={spacing.element_padding}
                          onChange={(e) =>
                            setSpacing((prev) => ({
                              ...prev,
                              element_padding: Number(e.target.value),
                            }))
                          }
                        />
                        <span className="absolute right-3 top-2.5 text-[10px] font-bold text-gray-400">
                          PX
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Typography Preview (Disabled for now) */}
              <Card className="rounded-3xl border-gray-100 shadow-sm opacity-60 bg-gray-50/30 overflow-hidden cursor-not-allowed group">
                <CardHeader className="bg-gray-50/50 border-b border-gray-100 px-8 py-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-white border border-gray-200 flex items-center justify-center shadow-sm">
                        <Type className="h-5 w-5 text-gray-400" />
                      </div>
                      <div>
                        <CardTitle className="text-xl font-bold flex items-center gap-2">
                          Typographies
                          <Badge className="bg-brand/10 text-brand border-none text-[8px] font-bold uppercase tracking-tighter">
                            Bientôt
                          </Badge>
                        </CardTitle>
                        <CardDescription>
                          Configurez vos polices (Google Fonts, Systèmes...)
                        </CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-8">
                  <div className="flex flex-col items-center justify-center py-4 space-y-3">
                    <Sparkles className="h-8 w-8 text-brand animate-pulse opacity-20" />
                    <p className="text-sm font-medium text-gray-400 text-center max-w-xs">
                      Nous travaillons sur l'intégration des Google Fonts pour
                      une personnalisation totale.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar: Live Preview & Actions */}
        <div className="lg:col-span-4 space-y-6">
          <Card className="rounded-3xl border-gray-100 shadow-lg shadow-gray-200/50 overflow-hidden sticky top-24">
            <CardHeader className="bg-gray-900 border-b border-gray-800 text-white p-6">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-brand/20 flex items-center justify-center border border-brand/20">
                  <Eye className="h-4 w-4 text-brand" />
                </div>
                <CardTitle className="text-base font-bold uppercase tracking-widest text-white/90">
                  Aperçu en direct
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {/* Live Document Preview */}
              <div
                className="p-6 border-b border-gray-100 transition-colors duration-300"
                style={{ backgroundColor: colors.background }}
              >
                {/* Header Section */}
                <div className="flex justify-between items-start mb-6">
                  <div className="space-y-1">
                    <div
                      className="text-sm font-bold tracking-widest uppercase"
                      style={{ color: colors.primary }}
                    >
                      DEVIS #2024-001
                    </div>
                    <div
                      className="text-[10px]"
                      style={{ color: colors.text_secondary }}
                    >
                      15 janvier 2024
                    </div>
                  </div>
                  <div
                    className="h-10 w-10 rounded-lg flex items-center justify-center text-[8px] font-bold uppercase"
                    style={{
                      backgroundColor: colors.secondary + '20',
                      color: colors.secondary,
                      border: `1px dashed ${colors.border}`,
                    }}
                  >
                    Logo
                  </div>
                </div>

                {/* Content Section */}
                <div className="space-y-3">
                  <div
                    className="text-xs font-semibold"
                    style={{ color: colors.text_primary }}
                  >
                    Votre entreprise
                  </div>
                  <div
                    className="text-[10px] leading-relaxed"
                    style={{ color: colors.text_secondary }}
                  >
                    123 Rue de la Startup
                    <br />
                    75001 Paris, France
                  </div>
                </div>

                {/* Table Preview */}
                <div
                  className="mt-6 rounded-lg overflow-hidden text-[9px]"
                  style={{ border: `1px solid ${colors.border}` }}
                >
                  <div
                    className="flex justify-between px-3 py-2 font-bold"
                    style={{
                      backgroundColor: colors.primary + '10',
                      color: colors.primary,
                    }}
                  >
                    <span>Description</span>
                    <span>Prix</span>
                  </div>
                  <div
                    className="flex justify-between px-3 py-2"
                    style={{
                      backgroundColor: colors.background,
                      color: colors.text_primary,
                      borderTop: `1px solid ${colors.border}`,
                    }}
                  >
                    <span>Prestation de service</span>
                    <span>1 500 €</span>
                  </div>
                </div>

                {/* Total */}
                <div
                  className="mt-4 flex justify-between items-center px-3 py-2 rounded-lg"
                  style={{
                    backgroundColor: colors.highlight + '15',
                    border: `1px solid ${colors.highlight}30`,
                  }}
                >
                  <span
                    className="text-[10px] font-bold uppercase"
                    style={{ color: colors.highlight }}
                  >
                    Total TTC
                  </span>
                  <span
                    className="text-sm font-bold"
                    style={{ color: colors.highlight }}
                  >
                    1 800 €
                  </span>
                </div>
              </div>

              {/* Color Summary */}
              <div className="p-6 bg-gray-50/50 space-y-4">
                <div className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-3">
                  Palette active
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(colors)
                    .filter(([key]) => !isColorLocked(key))
                    .map(([key, val]) => (
                      <div
                        key={key}
                        className="flex items-center gap-1.5 bg-white rounded-full px-2.5 py-1 border border-gray-100 shadow-sm"
                      >
                        <div
                          className="h-3 w-3 rounded-full border border-gray-200 shadow-sm"
                          style={{ backgroundColor: val }}
                        />
                        <span className="text-[9px] font-medium text-gray-500">
                          {COLOR_LABELS[key]?.split(' ')[0]}
                        </span>
                      </div>
                    ))}
                </div>

                <div className="pt-4">
                  <Button
                    type="submit"
                    disabled={isLoading || !name.trim()}
                    className="w-full bg-brand hover:bg-brand-dark shadow-lg shadow-brand/20 rounded-xl h-12 font-bold uppercase tracking-widest text-xs transition-all duration-300"
                  >
                    {isLoading ? (
                      <>
                        <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3" />
                        Sauvegarde...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        {submitLabel}
                      </>
                    )}
                  </Button>
                  <p className="text-[10px] text-center text-muted-foreground mt-4 italic">
                    Aperçu mis à jour en temps réel
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </form>
  );
}
