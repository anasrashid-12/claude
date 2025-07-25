'use client';

import { useEffect, useState } from 'react';

export default function useShop() {
  const [shop, setShop] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const url = new URL(window.location.href);
    const urlToken = url.searchParams.get('token');

    // ✅ Save token from URL to localStorage and clean URL
    if (urlToken) {
      localStorage.setItem('session', urlToken);
      const cleanUrl = `${url.origin}${url.pathname}`;
      window.history.replaceState({}, '', cleanUrl);
    }

    const fetchShop = async () => {
      const jwt = localStorage.getItem('session');
      if (!jwt) {
        if (isMounted) setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          headers: {
            Authorization: `Bearer ${jwt}`,
            Accept: 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(`Failed with status ${res.status}`);
        }

        const data = await res.json();
        if (isMounted) {
          setShop(data.shop || null);
          setToken(jwt);
        }
      } catch (error) {
        console.error('useShop error:', error);
        if (isMounted) {
          setShop(null);
          setToken(null);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchShop();

    return () => {
      isMounted = false;
    };
  }, []);

  return { shop, token, loading };
}
