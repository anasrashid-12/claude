// frontend/src/app/upload/page.tsx
'use client';

import { useState } from 'react';
import useShop from '@/hooks/useShop';
import ClientLayout from '../../../components/ClientLayout';
import {
  Page,
  Card,
  DropZone,
  Thumbnail,
  Button,
  Frame,
  Toast,
  Banner,
  Spinner,
  BlockStack,
} from '@shopify/polaris';

export default function UploadPage() {
  const { shop, loading: shopLoading } = useShop();
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const file = files[0];
  const previewUrl = file ? URL.createObjectURL(file) : null;

  const handleDrop = (_: unknown, accepted: File[]) => {
    setFiles(accepted);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file || !shop) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image', file);

      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const uploadData = await uploadRes.json();
      const imageUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/${uploadData.filename}`;

      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl, shop }),
      });

      const result = await processRes.json();
      if (result.success) {
        setToastVisible(true);
        setFiles([]);
      } else {
        setError('Failed to process image.');
      }
    } catch {
      setError('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  if (shopLoading) {
    return (
      <ClientLayout>
        <div className="p-6 text-gray-500">Loading shop session...</div>
      </ClientLayout>
    );
  }

  return (
    <ClientLayout>
      <Frame>
        <Page title="Upload Image">
          <Card>
            <BlockStack gap="400">
              <DropZone allowMultiple={false} onDrop={handleDrop}>
                {file && previewUrl ? (
                  <div className="flex items-center gap-2">
                    <Thumbnail size="large" source={previewUrl} alt="Preview" />
                    <div>{file.name}</div>
                  </div>
                ) : (
                  <DropZone.FileUpload actionTitle="Drop image or click to upload" />
                )}
              </DropZone>

              <div>
                <Button
                  onClick={handleUpload}
                  disabled={uploading || !file}
                  variant="primary"
                >
                  {uploading ? 'Uploading...' : 'Upload & Process'}
                </Button>
                {uploading && <Spinner accessibilityLabel="Uploading..." size="small" />}
              </div>

              {error && (
                <Banner title="Error" tone="critical">
                  <p>{error}</p>
                </Banner>
              )}
            </BlockStack>
          </Card>

          {toastVisible && (
            <Toast
              content="Image uploaded and queued for processing"
              onDismiss={() => setToastVisible(false)}
            />
          )}
        </Page>
      </Frame>
    </ClientLayout>
  );
}
