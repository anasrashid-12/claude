'use client';

import { useEffect, useState } from 'react';
import { Provider as AppBridgeProvider } from '@shopify/app-bridge-react';
import { AppProvider as PolarisProvider } from '@shopify/polaris';
import enTranslations from '@shopify/polaris/locales/en.json';
import '@shopify/polaris/build/esm/styles.css';
import { NavigationMenu } from '@shopify/app-bridge-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ImageProcessingDashboard } from '../components/ImageProcessingDashboard';

export default function HomePage() {
  const [config, setConfig] = useState<any>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop');

  useEffect(() => {
    if (!shop) {
      router.push('/login');
      return;
    }

    // Initialize App Bridge
    const host = searchParams.get('host');
    const config = {
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!,
      host: host!,
      forceRedirect: true
    };

    setConfig(config);
  }, [shop, router, searchParams]);

  if (!config) {
    return null;
  }

  return (
    <PolarisProvider i18n={enTranslations}>
      <AppBridgeProvider config={config}>
        <NavigationMenu
          navigationLinks={[
            {
              label: 'Dashboard',
              destination: '/',
            },
            {
              label: 'Settings',
              destination: '/settings',
            },
          ]}
        />
        <ImageProcessingDashboard />
      </AppBridgeProvider>
    </PolarisProvider>
  );
} 