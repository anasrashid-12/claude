// frontend/components/ProtectedLayout.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      const res = await fetch('/api/me');
      if (res.status === 200) {
        setLoading(false);
      } else {
        router.replace('/login');
      }
    };
    checkSession();
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;

  return <>{children}</>;
}
