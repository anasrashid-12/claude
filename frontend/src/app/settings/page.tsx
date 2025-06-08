import React, { useState, useEffect } from 'react';
import {
  Page,
  Card,
  FormLayout,
  TextField,
  Select,
  Button,
  Checkbox,
  Banner,
  Layout,
  Text,
} from '@shopify/polaris';

interface Settings {
  defaultProcessingType: string[];
  autoProcessNewProducts: boolean;
  maxImageSize: string;
  notificationEmail: string;
  storageRetentionDays: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    defaultProcessingType: ['background_removal'],
    autoProcessNewProducts: true,
    maxImageSize: '5',
    notificationEmail: '',
    storageRetentionDays: '30',
  });
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data);
    } catch (err) {
      setError('Failed to load settings');
    }
  };

  const handleSettingChange = (field: keyof Settings, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      setSuccessMessage('Settings saved successfully');
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Page title="Settings">
      <Layout>
        <Layout.Section>
          {error && (
            <Banner status="critical" onDismiss={() => setError(null)}>
              <p>{error}</p>
            </Banner>
          )}

          {successMessage && (
            <Banner status="success" onDismiss={() => setSuccessMessage(null)}>
              <p>{successMessage}</p>
            </Banner>
          )}

          <Card>
            <Card.Section>
              <Text variant="headingMd" as="h2">
                Image Processing Settings
              </Text>
            </Card.Section>

            <Card.Section>
              <FormLayout>
                <Select
                  label="Default Processing Type"
                  options={[
                    { label: 'Background Removal', value: 'background_removal' },
                    { label: 'Resize', value: 'resize' },
                    { label: 'Optimize', value: 'optimize' },
                  ]}
                  value={settings.defaultProcessingType[0]}
                  onChange={(value) =>
                    handleSettingChange('defaultProcessingType', [value])
                  }
                  helpText="Default processing type for new images"
                />

                <Checkbox
                  label="Automatically process new product images"
                  checked={settings.autoProcessNewProducts}
                  onChange={(checked) =>
                    handleSettingChange('autoProcessNewProducts', checked)
                  }
                  helpText="Process images automatically when new products are added"
                />

                <TextField
                  label="Maximum Image Size (MB)"
                  type="number"
                  value={settings.maxImageSize}
                  onChange={(value) => handleSettingChange('maxImageSize', value)}
                  helpText="Maximum allowed size for uploaded images"
                  autoComplete="off"
                />

                <TextField
                  label="Notification Email"
                  type="email"
                  value={settings.notificationEmail}
                  onChange={(value) =>
                    handleSettingChange('notificationEmail', value)
                  }
                  helpText="Email address for processing notifications"
                  autoComplete="email"
                />

                <TextField
                  label="Storage Retention (Days)"
                  type="number"
                  value={settings.storageRetentionDays}
                  onChange={(value) =>
                    handleSettingChange('storageRetentionDays', value)
                  }
                  helpText="Number of days to retain processed images"
                  autoComplete="off"
                />
              </FormLayout>
            </Card.Section>

            <Card.Section>
              <Button
                primary
                onClick={handleSave}
                loading={isSaving}
                disabled={isSaving}
              >
                Save Settings
              </Button>
            </Card.Section>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  );
} 