"use client";

import { useState } from "react";
import {
  Page,
  Card,
  DropZone,
  Text,
  Thumbnail,
  Stack,
  Button,
  Frame,
  Toast,
  Banner,
  Spinner,
} from "@shopify/polaris";
import { ImageIcon } from "@shopify/polaris-icons";

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrop = (_: any, acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);

    const file = files[0];
    const formData = new FormData();
    formData.append("image", file);

    try {
      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadRes.json();
      const imageUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/${uploadData.filename}`;

      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_url: imageUrl,
          shop: "ai-image-app-dev-store.myshopify.com", // ← Replace dynamically if needed
        }),
      });

      const result = await processRes.json();
      if (!result.success) throw new Error(result.detail || "Image queue failed");

      setToastVisible(true);
      setFiles([]);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Frame>
      <Page title="Upload Image">
        <Card sectioned>
          <DropZone allowMultiple={false} onDrop={handleDrop}>
            {files.length > 0 ? (
              <Stack alignment="center" spacing="tight">
                <Thumbnail
                  size="large"
                  source={window.URL.createObjectURL(files[0])}
                  alt="Uploaded image"
                />
                <div>{files[0].name}</div>
              </Stack>
            ) : (
              <DropZone.FileUpload actionTitle="Drop image file here or click to upload" />
            )}
          </DropZone>
          <div className="mt-4">
            <Button
              onClick={handleUpload}
              primary
              disabled={uploading || files.length === 0}
            >
              {uploading ? <Spinner size="small" /> : "Upload & Process"}
            </Button>
          </div>

          {error && (
            <div className="mt-4">
              <Banner title="Error" status="critical">
                <p>{error}</p>
              </Banner>
            </div>
          )}
        </Card>

        {toastVisible && (
          <Toast content="Image uploaded and queued for processing" onDismiss={() => setToastVisible(false)} />
        )}
      </Page>
    </Frame>
  );
}
