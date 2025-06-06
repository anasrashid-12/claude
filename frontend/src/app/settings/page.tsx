import React, { useState } from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  Button,
  BlockStack,
  Box,
  FormLayout,
  Select,
  TextField,
  ChoiceList,
  Banner
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
    maxImageSize: '10',
    notificationEmail: '',
    storageRetentionDays: '30'
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSettingChange = (field: keyof Settings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      // TODO: Implement API call to save settings
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setSaveSuccess(true);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Page
      title="Settings"
      primaryAction={
        <Button
          variant="primary"
          onClick={handleSave}
          loading={isSaving}
        >
          Save Changes
        </Button>
      }
    >
      <BlockStack>
        {saveSuccess && (
          <Banner
            title="Settings saved"
            tone="success"
            onDismiss={() => setSaveSuccess(false)}
          />
        )}

        <Layout>
          <Layout.Section>
            <Card>
              <Box padding="4">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Processing Settings
                  </Text>

                  <FormLayout>
                    <ChoiceList
                      title="Default Processing Types"
                      allowMultiple
                      choices={[
                        { label: 'Background Removal', value: 'background_removal' },
                        { label: 'Image Optimization', value: 'optimization' },
                        { label: 'Auto Resize', value: 'resize' }
                      ]}
                      selected={settings.defaultProcessingType}
                      onChange={(value) => handleSettingChange('defaultProcessingType', value)}
                    />

                    <ChoiceList
                      title="Auto-process New Products"
                      choices={[
                        { label: 'Automatically process images for new products', value: 'true' }
                      ]}
                      selected={settings.autoProcessNewProducts ? ['true'] : []}
                      onChange={(value) => handleSettingChange('autoProcessNewProducts', value.includes('true'))}
                    />

                    <TextField
                      label="Maximum Image Size (MB)"
                      type="number"
                      value={settings.maxImageSize}
                      onChange={(value) => handleSettingChange('maxImageSize', value)}
                      autoComplete="off"
                    />
                  </FormLayout>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          <Layout.Section>
            <Card>
              <Box padding="4">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Notification Settings
                  </Text>

                  <FormLayout>
                    <TextField
                      label="Notification Email"
                      type="email"
                      value={settings.notificationEmail}
                      onChange={(value) => handleSettingChange('notificationEmail', value)}
                      autoComplete="email"
                      helpText="Receive notifications when bulk processing is complete"
                    />
                  </FormLayout>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          <Layout.Section>
            <Card>
              <Box padding="4">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Storage Settings
                  </Text>

                  <FormLayout>
                    <TextField
                      label="Storage Retention Period (days)"
                      type="number"
                      value={settings.storageRetentionDays}
                      onChange={(value) => handleSettingChange('storageRetentionDays', value)}
                      autoComplete="off"
                      helpText="Number of days to keep processed images in storage"
                    />
                  </FormLayout>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>
        </Layout>
      </BlockStack>
    </Page>
  );
} 