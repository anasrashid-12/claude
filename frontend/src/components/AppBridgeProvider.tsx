'use client';

import { ReactNode, useEffect, useState, useMemo } from 'react';
import { Provider } from '@shopify/app-bridge-react';
import { useSearchParams } from 'next/navigation';
import { getCookie, setCookie } from 'cookies-next';

interface AppBridgeProviderProps {
  children: ReactNode;
}

export default function AppBridgeProvider({ children }: AppBridgeProviderProps) {
  const searchParams = useSearchParams();
  const [host, setHost] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!;
  const urlHost = searchParams.get('host');
  const urlShop = searchParams.get('shop');

  useEffect(() => {
    const cookieHost = getCookie('host') as string | undefined;
    const cookieShop = getCookie('shop') as string | undefined;

    if (urlHost) {
      setCookie('host', urlHost, { secure: true, sameSite: 'none' });
      setHost(urlHost);
    } else if (cookieHost) {
      setHost(cookieHost);
    } else {
      console.warn('⚠️ No host found in URL or cookie');
    }

    if (urlShop && !cookieShop) {
      setCookie('shop', urlShop, { secure: true, sameSite: 'none' });
    }

    setReady(true);
  }, [urlHost, urlShop]);

  const config = useMemo(() => {
    if (!host || !apiKey) return null;
    return { apiKey, host, forceRedirect: true };
  }, [host, apiKey]);

  if (!ready) {
    return <div className="p-4">⏳ Loading AppBridge...</div>;
  }

  if (!config) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500 text-center">
          ❌ AppBridge config missing. Open this app from your Shopify Admin.
        </p>
      </div>
    );
  }

  return <Provider config={config}>{children}</Provider>;
}
