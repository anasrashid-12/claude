// frontend/src/hooks/useAuth.ts
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function useAuth() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function fetchShop() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (!res.ok) throw new Error('Unauthorized');
        const data = await res.json();
        setShop(data.shop);
      } catch (err) {
        router.push('/login'); // Redirect to login if no session
      } finally {
        setLoading(false);
      }
    }

    fetchShop();
  }, [router]);

  return { shop, loading };
}