"use client";

import { useEffect, useState } from "react";
import {
  Page,
  Card,
  Text,
  Spinner,
  Badge,
  Thumbnail,
  Layout,
  EmptyState,
  Frame,
} from "@shopify/polaris";

interface ImageRecord {
  id: string;
  shop: string;
  image_url: string;
  processed_url: string | null;
  status: string;
  error_message?: string;
}

export default function QueuePage() {
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const shop = "ai-image-app-dev-store.myshopify.com"; // Replace dynamically if needed

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`
        );
        const data = await res.json();
        setImages(data.images || []);
      } catch (err) {
        console.error("Failed to fetch images", err);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
    const interval = setInterval(fetchImages, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const getBadge = (status: string) => {
    switch (status) {
      case "queued":
        return <Badge status="info">Queued</Badge>;
      case "processed":
        return <Badge status="success">Processed</Badge>;
      case "error":
        return <Badge status="critical">Error</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <Frame>
      <Page title="Image Queue">
        {loading ? (
          <div className="flex items-center justify-center p-8">
            <Spinner accessibilityLabel="Loading images" size="large" />
          </div>
        ) : images.length === 0 ? (
          <EmptyState
            heading="No images uploaded yet"
            image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/empty-state.svg"
          >
            <p>Upload images from the Upload tab to begin processing.</p>
          </EmptyState>
        ) : (
          <Layout>
            {images.map((img) => (
              <Layout.Section key={img.id} oneThird>
                <Card>
                  <Card.Section>
                    <Text variant="headingSm" as="h3">
                      {getBadge(img.status)}
                    </Text>
                  </Card.Section>
                  <Card.Section>
                    <Text as="p" tone="subdued">
                      Original:
                    </Text>
                    <Thumbnail
                      size="large"
                      source={img.image_url}
                      alt="Original image"
                    />
                  </Card.Section>
                  {img.status === "processed" && img.processed_url && (
                    <Card.Section>
                      <Text as="p" tone="subdued">
                        Processed:
                      </Text>
                      <Thumbnail
                        size="large"
                        source={img.processed_url}
                        alt="Processed image"
                      />
                    </Card.Section>
                  )}
                  {img.status === "error" && img.error_message && (
                    <Card.Section>
                      <Text tone="critical" as="p">
                        Error: {img.error_message}
                      </Text>
                    </Card.Section>
                  )}
                </Card>
              </Layout.Section>
            ))}
          </Layout>
        )}
      </Page>
    </Frame>
  );
}
