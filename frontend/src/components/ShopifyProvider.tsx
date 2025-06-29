'use client';

import { useEffect } from 'react';

export default function ShopifyProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const shop = searchParams.get('shop');
    const host = searchParams.get('host');

    const isEmbedded = window.top !== window.self;

    if (shop && !host) {
      const authUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/install?shop=${shop}`;
      if (isEmbedded) {
        window.top!.location.href = authUrl;
      } else {
        window.location.href = authUrl;
      }
    }
  }, []);

  return <>{children}</>;
}
