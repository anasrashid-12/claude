'use client';

import { PropsWithChildren, useMemo } from 'react';
import { createApp } from '@shopify/app-bridge';
import { usePathname, useSearchParams } from 'next/navigation';

export function AppBridgeProvider({ children }: PropsWithChildren) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  
  const app = useMemo(() => {
    // Early return if we're on the server
    if (typeof window === 'undefined') return null;

    const shop = searchParams.get('shop');
    const host = searchParams.get('host');

    // Check if we're embedded in Shopify
    const isEmbedded = window.self !== window.top;

    try {
      if (!shop) return null;

      if (!process.env.NEXT_PUBLIC_SHOPIFY_API_KEY) {
        console.error('Missing SHOPIFY_API_KEY environment variable');
        if (!isEmbedded) {
          window.location.href = `/api/auth?shop=${shop}`;
        }
        return null;
      }

      // Decode host parameter if it exists
      const decodedHost = host ? atob(host) : undefined;

      const config = {
        apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY,
        host: decodedHost || host || shop,
        forceRedirect: !isEmbedded
      };

      const app = createApp(config);
      return app;
    } catch (error) {
      console.error('Error initializing app:', error);
      if (!isEmbedded) {
        window.location.href = `/api/auth?shop=${shop}`;
      }
      return null;
    }
  }, [searchParams]);

  return <>{children}</>;
} 