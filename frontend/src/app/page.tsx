// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { AppProvider as PolarisProvider } from '@shopify/polaris';
import { createApp } from '@shopify/app-bridge';
import { Redirect } from '@shopify/app-bridge/actions';
import enTranslations from '@shopify/polaris/locales/en.json';
import '@shopify/polaris/build/esm/styles.css';
import Image from 'next/image'

function AppContent() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Shopify AI Image Processor
        </h1>
        <p className="text-xl text-gray-600">
          Transform your product images with AI-powered processing
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Background Removal</h2>
          <p className="text-gray-600 mb-4">
            Automatically remove backgrounds from your product images
          </p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Try Now
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Image Enhancement</h2>
          <p className="text-gray-600 mb-4">
            Enhance image quality and colors automatically
          </p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Try Now
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold mb-4">Batch Processing</h2>
          <p className="text-gray-600 mb-4">
            Process multiple images at once with our batch tools
          </p>
          <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Try Now
          </button>
        </div>
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
