// src/interface/components/quote/PdfPreviewPanel.tsx
export function PdfPreviewPanel({
  url,
  loading,
  error,
}: {
  url: string | null;
  loading: boolean;
  error: string | null;
}) {
  if (error)
    return <div className="text-red-600 text-sm">Erreur : {error}</div>;
  if (loading && !url)
    return <div className="text-sm text-gray-500">Génération du PDF…</div>;
  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: 8,
        overflow: 'hidden',
        background: '#fff',
      }}
    >
      {url ? (
        <object
          data={url}
          type="application/pdf"
          aria-label="Prévisualisation du devis"
          style={{ width: '100%', height: 700 }}
        >
          <p style={{ padding: 16 }}>
            Votre navigateur ne peut pas afficher le PDF ici.
            <a
              href={url}
              target="_blank"
              rel="noreferrer"
              style={{ marginLeft: 8, textDecoration: 'underline' }}
            >
              Ouvrir dans un nouvel onglet
            </a>
          </p>
        </object>
      ) : (
        <div style={{ padding: 16, color: '#6b7280' }}>
          Aucune prévisualisation disponible.
        </div>
      )}
    </div>
  );
}
