'use client';

import { ReactNode, useEffect, useState, useMemo } from 'react';
import { Provider } from '@shopify/app-bridge-react';
import { getCookie, setCookie } from 'cookies-next';
import { useSearchParams } from 'next/navigation';
import { getSupabase } from '../../utils/supabase/supabaseClient'; // ✅ import your shared Supabase client

interface AppBridgeProviderProps {
  children: ReactNode;
}

export default function AppBridgeProvider({ children }: AppBridgeProviderProps) {
  const searchParams = useSearchParams();
  const [host, setHost] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!;

  useEffect(() => {
    const supabase = getSupabase(); 

    const urlHost = searchParams.get('host');
    const urlShop = searchParams.get('shop');
    const cookieHost = getCookie('host') as string | undefined;
    const cookieShop = getCookie('shop') as string | undefined;

    const finalHost = cookieHost || urlHost;
    const finalShop = cookieShop || urlShop;

    if (finalHost) {
      setCookie('host', finalHost, { secure: true, sameSite: 'none' });
      setHost(finalHost);
    } else {
      console.warn('⚠️ No host found in cookies or URL');
    }

    if (finalShop) {
      setCookie('shop', finalShop, { secure: true, sameSite: 'none' });
    }

    setReady(true);
  }, [searchParams]);

  const config = useMemo(() => {
    if (!host) return null;
    return { apiKey, host, forceRedirect: true };
  }, [host, apiKey]);

  if (!ready) return <div className="p-4">⏳ Loading AppBridge...</div>;

  if (!config) {
    return (
      <div className="flex items-center justify-center h-screen text-center">
        <p className="text-red-500">
          ❌ Missing AppBridge config. Please open the app from your Shopify Admin.
        </p>
      </div>
    );
  }

  return <Provider config={config}>{children}</Provider>;
}
