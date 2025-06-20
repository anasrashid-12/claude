'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Checks if the user/shop is authenticated.
 * Redirects to /login if unauthenticated (by default).
 */
export default function useAuth(redirectTo = '/login') {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (!res.ok) throw new Error('Unauthorized');
        const data = await res.json();
        setShop(data.shop);
      } catch {
        console.warn('Unauthenticated - redirecting');
        router.push(redirectTo);
      } finally {
        setLoading(false);
      }
    };

    checkSession();
  }, [router, redirectTo]);

  return { shop, loading };
}
