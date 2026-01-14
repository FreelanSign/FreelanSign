import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { uploadAvatar } from '@/domain/user/api';

const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
const MAX_SIZE_MB = 2;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

type Props = {
  currentAvatarUrl?: string | null;
  onUploadSuccess?: (newUrl: string) => void;
};

export default function AvatarUpload({
  currentAvatarUrl,
  onUploadSuccess,
}: Props) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const displayUrl = previewUrl || currentAvatarUrl;

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);

    if (!ACCEPTED_TYPES.includes(file.type)) {
      setError('Format non supporté. Utilisez JPEG, PNG, WebP ou GIF.');
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setError(`Fichier trop volumineux. Maximum ${MAX_SIZE_MB} MB.`);
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (event) => {
      setPreviewUrl(event.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload
    handleUpload(file);
  }

  async function handleUpload(file: File) {
    setIsUploading(true);
    setError(null);

    try {
      const newUrl = await uploadAvatar(file);
      setPreviewUrl(null);
      onUploadSuccess?.(newUrl);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Erreur lors de l'upload";
      setError(message);
      setPreviewUrl(null);
    } finally {
      setIsUploading(false);
    }
  }

  function handleClick() {
    fileInputRef.current?.click();
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className="relative w-24 h-24 rounded-full overflow-hidden bg-muted cursor-pointer group"
        onClick={handleClick}
      >
        {displayUrl ? (
          <img
            src={displayUrl}
            alt="Avatar"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-muted-foreground text-3xl">
            ?
          </div>
        )}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <span className="text-white text-xs">Modifier</span>
        </div>
        {isUploading && (
          <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(',')}
        onChange={handleFileSelect}
        className="hidden"
      />

      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={handleClick}
        disabled={isUploading}
      >
        {isUploading ? 'Upload...' : 'Changer la photo'}
      </Button>

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
