'use client';

import { useEffect, useState } from 'react';
import { Provider as AppBridgeProvider } from '@shopify/app-bridge-react';
import { AppProvider as PolarisProvider, Page, Layout } from '@shopify/polaris';
import enTranslations from '@shopify/polaris/locales/en.json';
import '@shopify/polaris/build/esm/styles.css';
import { NavigationMenu } from '@shopify/app-bridge-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ImageProcessingDashboard } from '../components/ImageProcessingDashboard'; 

export default function HomePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [config, setConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const shop = searchParams.get('shop');
    const host = searchParams.get('host');

    if (!shop || !host) {
      router.push('/login');
      return;
    }

    const appBridgeConfig = {
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!,
      host,
      forceRedirect: true,
    };

    setConfig(appBridgeConfig);
    setLoading(false);
  }, [router, searchParams]);

  if (loading || !config) {
    return <div style={{ padding: '2rem' }}>🔄 Loading App...</div>;
  }

  return (
    <PolarisProvider i18n={enTranslations}>
      <AppBridgeProvider config={config}>
      <NavigationMenu
        navigationLinks={[
          { label: 'Dashboard', destination: '/' },
          { label: 'Image Gallery', destination: '/app/dashboard/image-gallery' },
          { label: 'Processing Queue', destination: '/app/dashboard/processing-queue' },
          { label: 'Settings', destination: '/app/dashboard/settings' },
        ]}
      />
        <Page title="AI Image Processing">
          <Layout>
            <Layout.Section>
              <ImageProcessingDashboard />
            </Layout.Section>
          </Layout>
        </Page>
      </AppBridgeProvider>
    </PolarisProvider>
  );
}
