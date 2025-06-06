// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { AppProvider as PolarisProvider } from '@shopify/polaris';
import { createApp } from '@shopify/app-bridge';
import { Redirect } from '@shopify/app-bridge/actions';
import enTranslations from '@shopify/polaris/locales/en.json';
import '@shopify/polaris/build/esm/styles.css';

function AppContent() {
  return (
    <div className="app-content">
      <div className="app-container p-6">
        <h1 className="text-2xl font-bold mb-4">Welcome to MaxFlow AI Image App</h1>
        <p className="mb-4">Start processing your product images with AI.</p>
      </div>
    </div>
  );
}

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true);
  const [appBridgeConfig, setAppBridgeConfig] = useState<{
    apiKey: string;
    host: string;
    forceRedirect: boolean;
  } | null>(null);

  useEffect(() => {
    // Check if we need to redirect to HTTPS
    if (typeof window !== 'undefined') {
      if (window.location.protocol === 'http:') {
        const httpsUrl = `https://${window.location.host}${window.location.pathname}${window.location.search}`;
        window.location.replace(httpsUrl);
        return;
      }

      // Get the host and API key
      const host = new URLSearchParams(window.location.search).get('host');
      const apiKey = process.env.NEXT_PUBLIC_SHOPIFY_API_KEY;

      if (host && apiKey) {
        const config = {
          host: host,
          apiKey: apiKey,
          forceRedirect: true,
        };

        setAppBridgeConfig(config);

        // Initialize App Bridge
        const app = createApp(config);

        // Set up redirect handler
        const redirect = Redirect.create(app);
        redirect.dispatch(Redirect.Action.REMOTE, window.location.href);
      }
    }

    setIsLoading(false);
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!appBridgeConfig) {
    return <div>Missing app configuration</div>;
  }

  return (
    <PolarisProvider i18n={enTranslations}>
      <AppContent />
    </PolarisProvider>
  );
}
