'use client';

import { useEffect, useState } from 'react';

export default function useShop() {
  const [shop, setShop] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // ✅ Save token from URL to localStorage if available
    const url = new URL(window.location.href);
    const urlToken = url.searchParams.get('token');
    if (urlToken) {
      localStorage.setItem('session', urlToken);
      const cleanUrl = `${url.origin}${url.pathname}`;
      window.history.replaceState({}, '', cleanUrl);
    }

    const fetchShop = async () => {
      const jwt = localStorage.getItem('session');
      if (!jwt) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          headers: {
            Authorization: `Bearer ${jwt}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setShop(data.shop);
          setToken(jwt);
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

  return { shop, token, loading };
}
