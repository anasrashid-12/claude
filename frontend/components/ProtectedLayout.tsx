'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
        credentials: 'include',
      });

      if (res.ok) {
        setLoading(false);
      } else {
        router.replace('/login');
      }
    };
    checkSession();
  }, [router]);

  if (loading) return <div className="p-6">Checking session...</div>;

  return <>{children}</>;
}
