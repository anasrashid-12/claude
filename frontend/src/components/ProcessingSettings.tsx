import { useState, useCallback } from 'react';
import {
  Card,
  Text,
  BlockStack,
  Select,
  RangeSlider,
  Button,
  InlineStack,
  Banner,
  Checkbox,
  FormLayout,
  TextField
} from '@shopify/polaris';

interface ProcessingSettings {
  quality: number;
  format: 'jpeg' | 'png' | 'webp';
  maxWidth: number;
  maxHeight: number;
  preserveMetadata: boolean;
  compressionLevel: number;
  backgroundRemoval: {
    enabled: boolean;
    threshold: number;
    refinement: number;
  };
  watermark: {
    enabled: boolean;
    text: string;
    opacity: number;
    position: 'center' | 'bottomRight' | 'bottomLeft' | 'topRight' | 'topLeft';
  };
}

const defaultSettings: ProcessingSettings = {
  quality: 85,
  format: 'webp',
  maxWidth: 2048,
  maxHeight: 2048,
  preserveMetadata: true,
  compressionLevel: 6,
  backgroundRemoval: {
    enabled: false,
    threshold: 0.5,
    refinement: 1
  },
  watermark: {
    enabled: false,
    text: '',
    opacity: 0.5,
    position: 'bottomRight'
  }
};

export default function ProcessingSettings() {
  const [settings, setSettings] = useState<ProcessingSettings>(defaultSettings);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const response = await fetch('/api/settings/processing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (!response.ok) throw new Error('Failed to save settings');
      
      setSuccessMessage('Settings saved successfully');
    } catch (err) {
      setError('Failed to save settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    setSettings(defaultSettings);
    setSuccessMessage(null);
    setError(null);
  };

  return (
    <Card>
      <BlockStack gap="400">
        <Text as="h2" variant="headingLg">Processing Settings</Text>

        {error && (
          <Banner tone="critical" onDismiss={() => setError(null)}>
            <p>{error}</p>
          </Banner>
        )}

        {successMessage && (
          <Banner tone="success" onDismiss={() => setSuccessMessage(null)}>
            <p>{successMessage}</p>
          </Banner>
        )}

        <FormLayout>
          <Select
            label="Output Format"
            options={[
              { label: 'JPEG', value: 'jpeg' },
              { label: 'PNG', value: 'png' },
              { label: 'WebP', value: 'webp' }
            ]}
            value={settings.format}
            onChange={(value) => setSettings(prev => ({ ...prev, format: value as ProcessingSettings['format'] }))}
          />

          <RangeSlider
            label="Quality"
            value={settings.quality}
            min={0}
            max={100}
            output
            onChange={(value: number) => setSettings(prev => ({ ...prev, quality: value }))}
          />

          <FormLayout.Group>
            <TextField
              type="number"
              label="Max Width"
              value={settings.maxWidth.toString()}
              onChange={(value) => setSettings(prev => ({ ...prev, maxWidth: parseInt(value, 10) }))}
              autoComplete="off"
            />
            <TextField
              type="number"
              label="Max Height"
              value={settings.maxHeight.toString()}
              onChange={(value) => setSettings(prev => ({ ...prev, maxHeight: parseInt(value, 10) }))}
              autoComplete="off"
            />
          </FormLayout.Group>

          <RangeSlider
            label="Compression Level"
            value={settings.compressionLevel}
            min={0}
            max={9}
            output
            onChange={(value: number) => setSettings(prev => ({ ...prev, compressionLevel: value }))}
          />

          <Checkbox
            label="Preserve Image Metadata"
            checked={settings.preserveMetadata}
            onChange={(checked) => setSettings(prev => ({ ...prev, preserveMetadata: checked }))}
          />

          <BlockStack gap="400">
            <Text as="h3" variant="headingMd">Background Removal</Text>
            
            <Checkbox
              label="Enable Background Removal"
              checked={settings.backgroundRemoval.enabled}
              onChange={(checked) => setSettings(prev => ({
                ...prev,
                backgroundRemoval: { ...prev.backgroundRemoval, enabled: checked }
              }))}
            />

            {settings.backgroundRemoval.enabled && (
              <BlockStack gap="400">
                <RangeSlider
                  label="Detection Threshold"
                  value={settings.backgroundRemoval.threshold}
                  min={0}
                  max={1}
                  step={0.1}
                  output
                  onChange={(value: number) => setSettings(prev => ({
                    ...prev,
                    backgroundRemoval: { ...prev.backgroundRemoval, threshold: value }
                  }))}
                />

                <RangeSlider
                  label="Edge Refinement"
                  value={settings.backgroundRemoval.refinement}
                  min={0}
                  max={2}
                  step={0.1}
                  output
                  onChange={(value: number) => setSettings(prev => ({
                    ...prev,
                    backgroundRemoval: { ...prev.backgroundRemoval, refinement: value }
                  }))}
                />
              </BlockStack>
            )}
          </BlockStack>

          <BlockStack gap="400">
            <Text as="h3" variant="headingMd">Watermark</Text>
            
            <Checkbox
              label="Enable Watermark"
              checked={settings.watermark.enabled}
              onChange={(checked) => setSettings(prev => ({
                ...prev,
                watermark: { ...prev.watermark, enabled: checked }
              }))}
            />

            {settings.watermark.enabled && (
              <BlockStack gap="400">
                <TextField
                  label="Watermark Text"
                  value={settings.watermark.text}
                  onChange={(value) => setSettings(prev => ({
                    ...prev,
                    watermark: { ...prev.watermark, text: value }
                  }))}
                  autoComplete="off"
                />

                <Select
                  label="Position"
                  options={[
                    { label: 'Center', value: 'center' },
                    { label: 'Bottom Right', value: 'bottomRight' },
                    { label: 'Bottom Left', value: 'bottomLeft' },
                    { label: 'Top Right', value: 'topRight' },
                    { label: 'Top Left', value: 'topLeft' }
                  ]}
                  value={settings.watermark.position}
                  onChange={(value) => setSettings(prev => ({
                    ...prev,
                    watermark: { ...prev.watermark, position: value as ProcessingSettings['watermark']['position'] }
                  }))}
                />

                <RangeSlider
                  label="Opacity"
                  value={settings.watermark.opacity}
                  min={0}
                  max={1}
                  step={0.1}
                  output
                  onChange={(value: number) => setSettings(prev => ({
                    ...prev,
                    watermark: { ...prev.watermark, opacity: value }
                  }))}
                />
              </BlockStack>
            )}
          </BlockStack>
        </FormLayout>

        <InlineStack gap="200" align="end">
          <Button onClick={handleReset}>Reset to Defaults</Button>
          <Button
            variant="primary"
            onClick={handleSave}
            loading={isSaving}
          >
            Save Settings
          </Button>
        </InlineStack>
      </BlockStack>
    </Card>
  );
} 