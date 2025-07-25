import { useEffect, useState } from 'react';

export default function useAuth() {
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include', // 👈 important to send cookie
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!res.ok) {
          throw new Error(`Auth failed: ${res.status}`);
        }

        const data = await res.json();
        setShop(data.shop);
      } catch (err: any) {
        console.error('useAuth error:', err);
        setError(err.message || 'Auth error');
      } finally {
        setLoading(false);
      }
    };

    fetchShop();
  }, []);

  return { shop, loading, error };
}
