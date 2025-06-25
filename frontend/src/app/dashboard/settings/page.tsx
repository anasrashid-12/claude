'use client';

import {
  Page,
  Card,
  Text,
  Checkbox,
  Button,
  Banner,
  Frame,
  Spinner,
  Toast,
  BlockStack,
  InlineStack,
} from '@shopify/polaris';
import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';
import ClientLayout from '../../../../components/ClientLayout';
import useShop from '@/hooks/useShop';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function SettingsPage() {
  const { shop, loading: shopLoading } = useShop();
  const [backgroundRemoval, setBackgroundRemoval] = useState(true);
  const [optimizeImages, setOptimizeImages] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toastActive, setToastActive] = useState(false);

  const fetchSettings = async () => {
    if (!shop) return;

    const { data, error: fetchError } = await supabase
      .from('settings')
      .select('*')
      .eq('shop', shop)
      .single();

    if (fetchError && fetchError.code !== 'PGRST116') {
      setError(fetchError.message);
    }

    if (data) {
      setBackgroundRemoval(data.background_removal);
      setOptimizeImages(data.optimize_images);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (!shop) return;
    fetchSettings();
  }, [shop]);

  const handleSave = async () => {
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
        <Page title="Settings">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <Spinner accessibilityLabel="Loading settings" size="large" />
            </div>
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

          {toastActive && (
            <Toast content="Settings saved" onDismiss={() => setToastActive(false)} />
          )}
        </Page>
      </Frame>
    </ClientLayout>
  );
}
