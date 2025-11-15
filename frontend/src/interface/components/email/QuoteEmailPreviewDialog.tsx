// frontend/src/interface/components/email/QuoteEmailPreviewDialog.tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogTitle,
} from '@/components/ui/dialog';
import { useEffect, useState } from 'react';
import { emailRepository } from '../../../infrastructure/email/emailRepository';
import styles from './quote-email-preview-dialog.module.css';

interface QuoteEmailPreviewDialogProps {
  quoteId: string;
  open: boolean;
  onClose: () => void;
}

export default function QuoteEmailPreviewDialog({
  quoteId,
  open,
  onClose,
}: QuoteEmailPreviewDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<{
    to: string;
    subject: string;
    body: string;
    attachment_link: string;
    template_version: string;
  } | null>(null);
  const [copiedField, setCopiedField] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    setLoading(true);
    setError(null);
    emailRepository
      .getPreparedEmail(quoteId)
      .then(setData)
      .catch((e) => {
        setError(e?.message || 'Erreur inconnue');
      })
      .finally(() => setLoading(false));
  }, [open, quoteId]);

  function copyToClipboard(text: string, fieldName: string) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        setCopiedField(fieldName);
        setTimeout(() => setCopiedField(null), 2000);
      })
      .catch(console.error);
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogOverlay className={styles.overlay} />
      <DialogContent className={styles.content}>
        <DialogTitle className={styles.title}>
          Prévisualisation de l'email
        </DialogTitle>
        <DialogDescription className={styles.description}>
          Copiez le contenu de l'email pour l'envoyer à votre client.
        </DialogDescription>

        <div className={styles.body}>
          {loading && <div className={styles.loading}>Chargement…</div>}

          {error && <div className={styles.error}>{error}</div>}

          {data && (
            <>
              <div className={styles.field}>
                <label className={styles.label}>Destinataire</label>
                <div className={styles.inputGroup}>
                  <textarea
                    readOnly
                    value={data.to}
                    rows={1}
                    className={styles.textarea}
                  />
                  <button
                    className={`${styles.buttonCopy} ${copiedField === 'to' ? styles.buttonCopied : ''}`}
                    onClick={() => copyToClipboard(data.to, 'to')}
                  >
                    {copiedField === 'to' ? '✓ Copié' : 'Copier'}
                  </button>
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Sujet</label>
                <div className={styles.inputGroup}>
                  <textarea
                    readOnly
                    value={data.subject}
                    rows={2}
                    className={styles.textarea}
                  />
                  <button
                    className={`${styles.buttonCopy} ${copiedField === 'subject' ? styles.buttonCopied : ''}`}
                    onClick={() => copyToClipboard(data.subject, 'subject')}
                  >
                    {copiedField === 'subject' ? '✓ Copié' : 'Copier'}
                  </button>
                </div>
              </div>

              <div className={styles.field}>
                <label className={styles.label}>Corps de l'email</label>
                <div className={styles.inputGroup}>
                  <textarea
                    readOnly
                    value={data.body}
                    rows={12}
                    className={`${styles.textarea} ${styles.textareaBody}`}
                  />
                  <button
                    className={`${styles.buttonCopy} ${copiedField === 'body' ? styles.buttonCopied : ''}`}
                    onClick={() => copyToClipboard(data.body, 'body')}
                  >
                    {copiedField === 'body' ? '✓ Copié' : 'Copier'}
                  </button>
                </div>
              </div>

              {data.attachment_link && (
                <div className={styles.field}>
                  <label className={styles.label}>Pièce jointe</label>
                  <div className={styles.inputGroup}>
                    <textarea
                      readOnly
                      value={data.attachment_link}
                      rows={1}
                      className={styles.textarea}
                    />
                    <button
                      className={`${styles.buttonCopy} ${copiedField === 'attachment' ? styles.buttonCopied : ''}`}
                      onClick={() =>
                        copyToClipboard(data.attachment_link, 'attachment')
                      }
                    >
                      {copiedField === 'attachment' ? '✓ Copié' : 'Copier'}
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className={styles.footer}>
          <button className={styles.buttonClose} onClick={onClose}>
            Fermer
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
