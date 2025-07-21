'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (res.ok) {
          setLoading(false);
        } else {
          router.replace('/login');
        }
      } catch (error) {
        console.error('Session check failed:', error);
        router.replace('/login');
      }
    };

    checkSession();
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-500 text-center p-4">
        🔐 Checking session...
      </div>
    );
  }

  return <>{children}</>;
}
