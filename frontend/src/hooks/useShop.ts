'use client';

import { useEffect, useState } from 'react';

export default function useShop() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });        

        if (res.ok) {
          const { shop } = await res.json();
          setShop(shop);
        } else {
          setShop(null);
        }
      } catch (error) {
        console.error('Error fetching shop info:', error);
        setShop(null);
      } finally {
        setLoading(false);
      }
    };

    fetchShop();
  }, []);

  return { shop, loading };
}
