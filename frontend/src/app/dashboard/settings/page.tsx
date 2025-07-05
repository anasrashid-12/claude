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
import ClientLayout from '@/components/ClientLayout';
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
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastActive, setToastActive] = useState(false);

  const fetchSettings = async () => {
    if (!shop) return;

    const { data, error: fetchError } = await supabase
      .from('settings')
      .select('*')
      .eq('shop', shop)
      .single();

    if (fetchError) {
      if (fetchError.code === 'PGRST116') {
        setBackgroundRemoval(true);
        setOptimizeImages(true);
      } else {
        setError(fetchError.message);
      }
    } else if (data) {
      setBackgroundRemoval(data.background_removal ?? true);
      setOptimizeImages(data.optimize_images ?? true);
    }

    setLoading(false);
  };

  useEffect(() => {
    if (shop) fetchSettings();
  }, [shop]);

  const handleSave = async () => {
    if (!shop) {
      setError('Shop not found. Please reload the page.');
      return;
    }

    setSaving(true);

    const { error: upsertError } = await supabase.from('settings').upsert({
      shop,
      background_removal: backgroundRemoval,
      optimize_images: optimizeImages,
    });

    setSaving(false);

    if (upsertError) {
      setError(upsertError.message);
    } else {
      setToastActive(true);
    }
  };

  return (
    <ClientLayout>
      <Frame>
        <Page title="⚙️ App Settings">
          {loading || shopLoading ? (
            <div className="flex justify-center items-center h-64">
              <Spinner accessibilityLabel="Loading settings" size="large" />
            </div>
          ) : (
            <div className="max-w-2xl mx-auto px-4">
              <Card padding="400">
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
                    <Button
                      variant="primary"
                      onClick={handleSave}
                      loading={saving}
                    >
                      Save Settings
                    </Button>
                  </InlineStack>
                </BlockStack>
              </Card>
            </div>
          )}

          {error && (
            <div className="max-w-2xl mx-auto mt-4 px-4">
              <Banner
                title="Something went wrong"
                tone="critical"
                onDismiss={() => setError(null)}
              >
                <p>{error}</p>
              </Banner>
            </div>
          )}

          {toastActive && (
            <Toast
              content="✅ Settings saved successfully"
              onDismiss={() => setToastActive(false)}
            />
          )}
        </Page>
      </Frame>
    </ClientLayout>
  );
}
