'use client';

import { useEffect, useState } from 'react';
import {
  Card,
  Page,
  Layout,
  Text,
  InlineStack,
  Button,
  Checkbox,
  Frame,
  Toast,
  BlockStack,
  Spinner,
  Banner,
} from '@shopify/polaris';
import { createClient } from '@supabase/supabase-js';
import ClientLayout from '../../../../components/ClientLayout'; // ✅ Polaris wrapper

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function SettingsPage() {
  const [backgroundRemoval, setBackgroundRemoval] = useState(true);
  const [optimizeImages, setOptimizeImages] = useState(true);
  const [toastActive, setToastActive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [shop, setShop] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchShopAndSettings = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });

        if (!res.ok) throw new Error('Authentication failed');

        const data: { shop: string } = await res.json();
        setShop(data.shop);

        const { data: settings, error: fetchError } = await supabase
          .from('settings')
          .select('*')
          .eq('shop', data.shop)
          .single();

        if (fetchError && fetchError.code !== 'PGRST116') {
          throw new Error(fetchError.message);
        }

        if (settings) {
          setBackgroundRemoval(settings.background_removal);
          setOptimizeImages(settings.optimize_images);
        }
      } catch (e) {
        const err = e as Error;
        setError(err.message || 'Failed to load settings');
      } finally {
        setLoading(false);
      }
    };

    fetchShopAndSettings();
  }, []);

  const handleSave = async () => {
    if (!shop) {
      setError('Shop not found. Please re-authenticate.');
      return;
    }

    const { error: upsertError } = await supabase.from('settings').upsert({
      shop,
      background_removal: backgroundRemoval,
      optimize_images: optimizeImages,
    });

    if (upsertError) {
      setError(upsertError.message);
    } else {
      setToastActive(true);
    }
  };

  return (
    <ClientLayout>
      <Frame>
        <Page title="Image Processing Settings">
          <Layout>
            <Layout.Section>
              {loading ? (
                <Spinner accessibilityLabel="Loading settings..." size="large" />
              ) : (
                <Card>
                  <BlockStack gap="400">
                    <Text as="h2" variant="headingMd">
                      Preferences
                    </Text>

                    <BlockStack gap="200">
                      <Checkbox
                        label="Remove background from images"
                        checked={backgroundRemoval}
                        onChange={() => setBackgroundRemoval(!backgroundRemoval)}
                      />
                      <Checkbox
                        label="Optimize images for web"
                        checked={optimizeImages}
                        onChange={() => setOptimizeImages(!optimizeImages)}
                      />
                    </BlockStack>

                    <InlineStack align="end">
                      <Button variant="primary" onClick={handleSave}>
                        Save Settings
                      </Button>
                    </InlineStack>
                  </BlockStack>
                </Card>
              )}

              {error && (
                <Banner title="Error" tone="critical">
                  <p>{error}</p>
                </Banner>
              )}
            </Layout.Section>
          </Layout>

          {toastActive && (
            <Toast
              content="Settings saved"
              onDismiss={() => setToastActive(false)}
            />
          )}
        </Page>
      </Frame>
    </ClientLayout>
  );
}
