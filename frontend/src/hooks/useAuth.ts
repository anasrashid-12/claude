import { useEffect, useState } from 'react';

export default function useAuth() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include', // Important for sending cookies
          headers: {
            Accept: 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(`Auth failed: ${res.status}`);
        }

        const data = await res.json();

        if (isMounted) {
          setShop(data.shop);
        }
      } catch (err: any) {
        console.error('useAuth error:', err);
        if (isMounted) {
          setError(err.message || 'Authentication error');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchShop();

    return () => {
      isMounted = false;
    };
  }, []);

  return { shop, loading, error };
}
