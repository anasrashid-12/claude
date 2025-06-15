// frontend/app/settings/page.tsx
"use client";

import { useState } from "react";
import { Card, Page, Layout, Text, InlineStack, Button, Checkbox, Frame, Toast } from "@shopify/polaris";

export default function SettingsPage() {
  const [backgroundRemoval, setBackgroundRemoval] = useState(true);
  const [optimizeImages, setOptimizeImages] = useState(true);
  const [toastActive, setToastActive] = useState(false);

  const handleSave = () => {
    // TODO: Save to Supabase or localStorage
    setToastActive(true);
  };

  return (
    <Frame>
      <Page title="Image Processing Settings">
        <Layout>
          <Layout.Section>
            <Card sectioned>
              <Text as="h2" variant="headingMd">
                Preferences
              </Text>
              <InlineStack gap="4" wrap={false}>
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
              </InlineStack>
              <Button onClick={handleSave} variant="primary" className="mt-4">
                Save Settings
              </Button>
            </Card>
          </Layout.Section>
        </Layout>

        {toastActive && (
          <Toast content="Settings saved" onDismiss={() => setToastActive(false)} />
        )}
      </Page>
    </Frame>
  );
}
