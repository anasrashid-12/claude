'use client';

import { useState, useEffect } from 'react';
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
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleDrop = (_dropFiles: unknown, acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    const file = files[0];
    const formData = new FormData();
    formData.append('image', file);

    try {
      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const uploadData = await uploadRes.json();
      const imageUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/${uploadData.filename}`;

      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_url: imageUrl,
          shop: 'ai-image-app-dev-store.myshopify.com',
        }),
      });

      const result = await processRes.json();
      if (!result.success) throw new Error(result.detail || 'Image queue failed');

      setToastVisible(true);
      setFiles([]);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Upload failed');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <Frame>
      <Page title="Upload Image">
        <Card>
          <BlockStack gap="400">
            <DropZone allowMultiple={false} onDrop={handleDrop}>
              {files.length > 0 && isClient ? (
                <div className="flex items-center gap-2">
                  <Thumbnail
                    size="large"
                    source={URL.createObjectURL(files[0])}
                    alt="Uploaded image"
                  />
                  <div>{files[0].name}</div>
                </div>
              ) : (
                <DropZone.FileUpload actionTitle="Drop image file here or click to upload" />
              )}
            </DropZone>

            <div>
              <Button
                onClick={handleUpload}
                disabled={uploading || files.length === 0}
              >
                {uploading ? 'Uploading...' : 'Upload & Process'}
              </Button>
              {uploading && (
                <div className="mt-2">
                  <Spinner size="small" accessibilityLabel="Uploading..." />
                </div>
              )}
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
  );
}
