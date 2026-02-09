// components/feedback/FeedbackButton.tsx
import { MessageSquare } from 'lucide-react';
import { useState } from 'react';
import { Button } from '../ui/button';
import { FeedbackModal } from './FeedbackModal';

export function FeedbackButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="outline"
        size="icon"
        className="fixed bottom-6 right-6 z-50 h-12 w-12 rounded-full shadow-lg hover:shadow-xl transition-shadow bg-white"
        onClick={() => setOpen(true)}
        aria-label="Envoyer un feedback"
      >
        <MessageSquare className="h-5 w-5" />
      </Button>
      <FeedbackModal open={open} onClose={() => setOpen(false)} />
    </>
  );
}
