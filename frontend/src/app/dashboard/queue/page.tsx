'use client';

import { useEffect, useState } from 'react';
import ClientLayout from '../../../../components/ClientLayout';
import {
  Page,
  Card,
  Text,
  Spinner,
  Badge,
  Thumbnail,
  Grid,
  EmptyState,
  Frame,
  Box,
} from '@shopify/polaris';

interface ImageRecord {
  id: string;
  shop: string;
  image_url: string;
  processed_url: string | null;
  status: string;
  error_message?: string;
}

export default function QueuePage() {
  const [shop, setShop] = useState<string | null>(null);
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          credentials: 'include',
        });
        const data = await res.json();
        if (data?.shop) {
          setShop(data.shop);
        } else {
          throw new Error('No shop returned');
        }
      } catch (error) {
        console.error('❌ Error fetching shop info:', error);
        setShop(null);
        setLoading(false);
      }
    };

    fetchShop();
  }, []);

  useEffect(() => {
    if (!shop) return;

    const fetchImages = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`
        );
        const data = await res.json();
        setImages(data.images || []);
      } catch (err) {
        console.error('❌ Error fetching images:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
    const interval = setInterval(fetchImages, 5000);
    return () => clearInterval(interval);
  }, [shop]);

  const getBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'queued':
        return <Badge tone="info">Queued</Badge>;
      case 'processing':
        return <Badge tone="attention">Processing</Badge>;
      case 'processed':
      case 'completed':
        return <Badge tone="success">Processed</Badge>;
      case 'error':
      case 'failed':
        return <Badge tone="critical">Error</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <ClientLayout>
      <Frame>
        <Page title="Image Queue">
          {loading ? (
            <div className="flex justify-center items-center p-10">
              <Spinner accessibilityLabel="Loading images" size="large" />
            </div>
          ) : !shop ? (
            <EmptyState
              heading="Shop not authenticated"
              image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/empty-state.svg"
            >
              <p>Please login again to continue.</p>
            </EmptyState>
          ) : images.length === 0 ? (
            <EmptyState
              heading="No images in the queue"
              image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/empty-state.svg"
            >
              <p>Upload an image to get started.</p>
            </EmptyState>
          ) : (
            <Grid columns={{ xs: 1, sm: 2, md: 3 }}>
              {images.map((img) => (
                <Box key={img.id} padding="300">
                  <Card>
                    <Box padding="200">
                      <Text variant="headingSm" as="h3">
                        {getBadge(img.status)}
                      </Text>

                      <Box paddingBlockStart="200">
                        <Text as="p" tone="subdued">Original:</Text>
                        <Thumbnail
                          size="large"
                          source={img.image_url}
                          alt={`Original image ${img.id}`}
                        />
                      </Box>

                      {['processed', 'completed'].includes(img.status) && img.processed_url && (
                        <Box paddingBlockStart="200">
                          <Text as="p" tone="subdued">Processed:</Text>
                          <Thumbnail
                            size="large"
                            source={img.processed_url}
                            alt={`Processed image ${img.id}`}
                          />
                        </Box>
                      )}

                      {['processed', 'completed'].includes(img.status) && !img.processed_url && (
                        <Box paddingBlockStart="200">
                          <Text tone="critical" as="p">
                            Processed URL missing
                          </Text>
                        </Box>
                      )}

                      {['error', 'failed'].includes(img.status) && (
                        <Box paddingBlockStart="200">
                          <Text tone="critical" as="p">
                            Error: {img.error_message || 'Unknown error'}
                          </Text>
                        </Box>
                      )}
                    </Box>
                  </Card>
                </Box>
              ))}
            </Grid>
          )}
        </Page>
      </Frame>
    </ClientLayout>
  );
}
