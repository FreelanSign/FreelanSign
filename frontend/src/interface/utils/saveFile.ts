// src/interface/utils/saveFile.ts

interface FilePickerOptions {
  suggestedName?: string;
  types?: Array<{
    description?: string;
    accept: Record<string, string[]>;
  }>;
}

interface WindowWithFilePicker extends Window {
  showSaveFilePicker?: (options?: FilePickerOptions) => Promise<{
    createWritable: () => Promise<{
      write: (data: Blob) => Promise<void>;
      close: () => Promise<void>;
    }>;
  }>;
}

export async function saveBlobUrlAs(blobUrl: string, suggestedName: string) {
  // Récupère le Blob depuis l'URL blob:
  const resp = await fetch(blobUrl);
  const blob = await resp.blob();

  // 1) File System Access API (Chromium, Safari récent)
  const extendedWindow = window as WindowWithFilePicker;
  if (typeof extendedWindow.showSaveFilePicker === 'function') {
    const handle = await extendedWindow.showSaveFilePicker({
      suggestedName,
      types: [
        {
          description: 'PDF',
          accept: { 'application/pdf': ['.pdf'] },
        },
      ],
    });
    const writable = await handle.createWritable();
    await writable.write(blob);
    await writable.close();
    return;
  }

  // 2) Fallback: téléchargement classique (dossier par défaut du navigateur)
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = suggestedName;
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  a.remove();
}

// Petit helper pour proposer d'ouvrir dans un nouvel onglet
export function openBlobUrlInNewTab(blobUrl: string) {
  const w = window.open(blobUrl, '_blank', 'noopener');
  if (!w) {
    // popup bloqué : on propose un téléchargement classique
    const a = document.createElement('a');
    a.href = blobUrl;
    a.target = '_blank';
    a.rel = 'noopener';
    a.click();
  }
}
