'use client';

import { useEffect, useState } from 'react';

export default function useAuth() {
  const [authenticated, setAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch('/api/me', {
          credentials: 'include',
        });

        if (res.ok) {
          const { shop } = await res.json();
          setAuthenticated(!!shop);
        } else {
          setAuthenticated(false);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  return { authenticated, loading };
}
