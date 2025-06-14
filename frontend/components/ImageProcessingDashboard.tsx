'use client';

import {
  Page,
  Layout,
  Card,
  DropZone,
  Thumbnail,
  Text,
  Banner,
  Spinner,
  EmptyState,
  BlockStack,
  Frame,
  Toast,
  Box,
} from '@shopify/polaris';
import { useState, useCallback } from 'react';

export function ImageProcessingDashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [processedImageUrl, setProcessedImageUrl] = useState<string | null>(null);
  const [toastProps, setToastProps] = useState<{ content: string; error?: boolean } | null>(null);

  const showToast = useCallback((content: string, error = false) => {
    setToastProps({ content, error });
  }, []);

  const dismissToast = useCallback(() => {
    setToastProps(null);
  }, []);

  const handleDrop = useCallback((files: File[]) => {
    setFile(files[0]);
    setProcessedImageUrl(null); // Reset previous image
  }, []);

  const handleUpload = async () => {
    if (!file) {
      showToast('Please select a file first', true);
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setProcessedImageUrl(data.processed_url); // returned from AI service
      showToast('Image uploaded & processed');
    } catch (error) {
      console.error(error);
      showToast('Error uploading image', true);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Frame>
      <Page title="Upload Image for AI Processing">
        <Layout>
          <Layout.Section>
          <Card>
            <Box padding="400">
              <BlockStack gap="400">
                <DropZone accept="image/*" type="image" onDrop={handleDrop}>
                  {file ? (
                    <DropZone.FileUpload />
                  ) : (
                    <DropZone.FileUpload actionTitle="Drop image here or click to upload" />
                  )}
                </DropZone>

                {file && (
                  <div style={{ textAlign: 'center' }}>
                    <Thumbnail size="large" source={URL.createObjectURL(file)} alt={file.name} />
                    <Text as="p" variant="bodyMd" fontWeight="medium">
                      {file.name}
                    </Text>
                    <button
                      style={{
                        marginTop: '1rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#229799',
                        color: 'white',
                        border: 'none',
                        borderRadius: 4,
                        cursor: 'pointer',
                      }}
                      onClick={handleUpload}
                      disabled={uploading}
                    >
                      {uploading ? 'Processing...' : 'Start Processing'}
                    </button>
                  </div>
                )}

                {uploading && <Spinner accessibilityLabel="Uploading" size="large" />}
                {processedImageUrl && (
                  <Banner title="Processed Image" tone="success">
                    <img
                      src={processedImageUrl}
                      alt="Processed"
                      style={{ marginTop: 10, maxWidth: '100%' }}
                    />
                  </Banner>
                )}
              </BlockStack>
            </Box>
          </Card>
          </Layout.Section>
        </Layout>

        {toastProps && (
          <Toast
            content={toastProps.content}
            error={toastProps.error}
            onDismiss={dismissToast}
          />
        )}
      </Page>
    </Frame>
  );
}
