'use client';

import {
  Page,
  Layout,
  Card,
  TextField,
  Select,
  Button,
  Frame,
  Toast,
  BlockStack,
  Text,
} from '@shopify/polaris';
import { useState } from 'react';
import { useAuthenticatedFetch } from '../hooks/useAuthenticatedFetch';

export default function Settings() {
  const fetch = useAuthenticatedFetch();
  const [defaultType, setDefaultType] = useState('background_removal');
  const [apiKey, setApiKey] = useState('');
  const [toast, setToast] = useState(false);

  const saveSettings = async () => {
    await fetch('/api/v1/settings', {
      method: 'POST',
      body: JSON.stringify({ defaultType, apiKey }),
      headers: { 'Content-Type': 'application/json' },
    });
    setToast(true);
  };

  return (
    <Frame>
      <Page title="App Settings">
        <Layout>
          <Layout.Section>
            <Card>
              <BlockStack gap="400">
                <Text variant="headingMd" as="h6">App Settings</Text>
                <Select
                  label="Processing Type"
                  options={[
                    { label: 'Background Removal', value: 'background_removal' },
                    { label: 'Enhancement', value: 'enhancement' },
                    { label: 'Format Conversion', value: 'format_conversion' },
                  ]}
                  onChange={setDefaultType}
                  value={defaultType}
                />
                <TextField
                  label="AI API Key"
                  value={apiKey}
                  onChange={setApiKey}
                  autoComplete='off'
                />
                <Button onClick={saveSettings} variant="primary">Save</Button>
              </BlockStack>
            </Card>
          </Layout.Section>
        </Layout>
        {toast && <Toast content="Settings saved!" onDismiss={() => setToast(false)} />}
      </Page>
    </Frame>
  );
}
