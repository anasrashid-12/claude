'use client';
import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function TopLevelRedirectPage() {
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop');
  const host = searchParams.get('host');

  useEffect(() => {
    if (typeof window !== 'undefined' && shop && host) {
      const redirectUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/oauth?shop=${shop}&host=${host}`;
      
      // Only redirect if inside an iframe
      if (window.top && window.top !== window.self) {
        window.top.location.href = redirectUrl;
      } else {
        window.location.href = redirectUrl;
      }
    }
  }, [shop, host]);

  return <div className="p-4">🚀 Redirecting to Shopify...</div>;
}
