'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const shop = searchParams.get('shop');
    const host = searchParams.get('host');

    const checkAuth = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (res.ok) {
          router.replace('/dashboard');
        } else {
          // Pass shop & host to login so cookies can be set
          if (shop && host) {
            router.replace(`/login?shop=${shop}&host=${host}`);
          } else {
            router.replace('/login');
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        router.replace('/login');
      }
    };

    checkAuth();
  }, [router, searchParams]);

  return (
    <div className="flex items-center justify-center h-screen">
      <h1 className="text-2xl">Redirecting...</h1>
    </div>
  );
}
