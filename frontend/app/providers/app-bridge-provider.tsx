'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { createApp, AppConfig } from '@shopify/app-bridge';
import { AppBridgeContext } from '@shopify/app-bridge-react/context';

export function AppBridgeProvider({ children }: { children: React.ReactNode }) {
  const [appBridge, setAppBridge] = useState<any>(null);
  const [host, setHost] = useState<string | null>(null);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const hostParam = searchParams.get('host');
    if (hostParam) {
      setHost(hostParam);
    }
  }, []);

  const appBridgeConfig: AppConfig | null = useMemo(() => {
    if (!host) return null;
    return {
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!,
      host,
      forceRedirect: true,
    };
  }, [host]);

  useEffect(() => {
    if (appBridgeConfig && !appBridge) {
      const app = createApp(appBridgeConfig);
      setAppBridge(app);
    }
  }, [appBridgeConfig]);

  if (!appBridge) return null;

  return (
    <AppBridgeContext.Provider value={appBridge}>
      {children}
    </AppBridgeContext.Provider>
  );
}
