// apps/interface/hooks/useThemes.ts
import { useEffect, useState } from 'react';
import {
  themeRepository,
  type ThemeListItem,
} from '../../infrastructure/branding/themeRepository';

export function useThemes() {
  const [themes, setThemes] = useState<ThemeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await themeRepository.listMine();
        if (!mounted) return;
        setThemes(list);
      } catch (err: unknown) {
        if (!mounted) return;
        setError(err);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return { themes, loading, error, setThemes };
}
