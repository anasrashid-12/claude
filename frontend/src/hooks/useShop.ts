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
          const errText = await res.text();
          throw new Error(`Auth failed: ${res.status} - ${errText}`);
        }

        const data = await res.json();
        if (isMounted && data?.shop) {
          setShop(data.shop);
        } else {
          throw new Error('No shop found in response');
        }
      } catch (err: any) {
        console.error('[useShop] Error:', err);
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
