"use client";

import { useEffect, useState } from 'react';

export default function useShop() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchShop() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });
        if (!res.ok) throw new Error('Not authenticated');
        const data = await res.json();
        setShop(data.shop);
      } catch (err) {
        setShop(null);
      } finally {
        setLoading(false);
      }
    }
    fetchShop();
  }, []);

  return { shop, loading };
}
