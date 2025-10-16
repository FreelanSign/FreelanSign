// src/interface/components/common/Modal.tsx
import React, { useEffect } from 'react';
import './Modal.css';

type Props = {
  open: boolean;
  onClose: () => void;
  title?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  maxWidth?: number;
};

export default function Modal({
  open,
  onClose,
  title,
  actions,
  children,
  maxWidth = 980,
}: Props) {
  useEffect(() => {
    function onEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    if (open) document.addEventListener('keydown', onEsc);
    return () => document.removeEventListener('keydown', onEsc);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      onClick={onClose}
      className="fs-modal-backdrop"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="fs-modal"
        style={{ ['--fs-modal-maxw' as unknown as string]: `${maxWidth}px` }}
      >
        <div className="fs-modal__header">
          <h3 className="fs-modal__title">{title ?? 'Aperçu'}</h3>
          <div className="fs-modal__actions">
            {actions}
            <button
              onClick={onClose}
              aria-label="Fermer"
              className="fs-modal__close"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-x"
              >
                <path d="M18 6 6 18"></path>
                <path d="m6 6 12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        <div className="fs-modal__body">{children}</div>
      </div>
    </div>
  );
}
