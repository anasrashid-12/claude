// frontend/components/ProtectedLayout.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch('/api/me');
        if (res.status === 200) {
          setLoading(false);
        } else {
          router.replace('/login');
        }
      } catch (err) {
        console.error('Session check failed:', err);
        router.replace('/login');
      }
    };

    checkSession();
  }, [router]);

  if (loading) return <div className="p-6 text-gray-600">Checking session...</div>;

  return <>{children}</>;
}
