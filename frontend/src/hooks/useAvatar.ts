'use client';

import { useEffect, useState } from 'react';
import useShop from './useShop';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function useAvatar() {
  const { shop } = useShop();
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!shop) return;

    const fetchSignedUrl = async () => {
      try {
        setLoading(true);
        const res = await fetch(`${BACKEND_URL}/settings/avatar/refresh`, {
          credentials: 'include',
        });
        if (!res.ok) return;
        const data = await res.json();
        setAvatarUrl(data.url);
      } catch (err) {
        console.error('Failed to refresh avatar URL', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSignedUrl();
    const interval = setInterval(fetchSignedUrl, 1000 * 60 * 60 * 24 * 6); // every 6 days
    return () => clearInterval(interval);
  }, [shop]);

  return { avatarUrl, loading };
}
