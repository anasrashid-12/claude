// frontend/src/hooks/useShop.ts
'use client';

import { useEffect, useState } from 'react';

interface UseShopResult {
  shop: string | null;
  loading: boolean;
  error: string | null;
}

export default function useShop(): UseShopResult {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          method: 'GET',
          credentials: 'include',
          headers: {
            Accept: 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(`Auth failed: ${res.status}`);
        }

        const data = await res.json();
        if (isMounted) setShop(data.shop || null);
      } catch (err: any) {
        console.warn('[useShop] Error:', err.message || err);
        if (isMounted) setError(err.message || 'Authentication error');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchShop();

    return () => {
      isMounted = false;
    };
  }, []);

  return { shop, loading, error };
}
