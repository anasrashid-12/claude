'use client';

import { useEffect, useState } from 'react';

export default function useShop() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (!res.ok) throw new Error('Unauthenticated');
        const data = await res.json();
        setShop(data.shop);
      } catch {
        console.warn('[useShop] ❌ Failed to fetch shop session');
        setShop(null);
      } finally {
        setLoading(false);
      }
    };

    fetchShop();
  }, []);

  return { shop, loading };
}
