'use client';

import ClientLayout from '@/components/ClientLayout';
import useShop from '@/hooks/useShop';
import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';
import {
  Badge,
  Card,
  Frame,
  Grid,
  Page,
  Text,
  EmptyState,
  Spinner,
  Thumbnail,
  BlockStack,
  Box,
} from '@shopify/polaris';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface ImageRecord {
  id: string;
  image_url: string;
  processed_url: string | null;
  status: string;
  error_message?: string;
}

export default function QueuePage() {
  const { shop, loading: shopLoading } = useShop();
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchImages = async () => {
    if (!shop) return;
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`,
        { credentials: 'include' }
      );
      const data = await res.json();
      setImages(data.images || []);
    } catch (error) {
      console.error('❌ Error fetching images:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!shop) return;

    fetchImages();

    const channel = supabase
      .channel(`realtime:images-${shop}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'images',
          filter: `shop=eq.${shop}`,
        },
        (payload) => {
          const newRecord = payload.new as ImageRecord;
          const eventType = payload.eventType;

          if (eventType === 'INSERT') {
            setImages((prev) => [newRecord, ...prev]);
          } else if (eventType === 'UPDATE') {
            setImages((prev) =>
              prev.map((img) => (img.id === newRecord.id ? newRecord : img))
            );
          } else if (eventType === 'DELETE') {
            const deletedId = (payload.old as ImageRecord).id;
            setImages((prev) => prev.filter((img) => img.id !== deletedId));
          }
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [shop]);

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'queued':
      case 'pending':
        return <Badge tone="info">Queued</Badge>;
      case 'processing':
        return <Badge tone="attention">Processing</Badge>;
      case 'processed':
      case 'completed':
        return <Badge tone="success">Processed</Badge>;
      case 'failed':
      case 'error':
        return <Badge tone="critical">Failed</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  if (shopLoading || loading) {
    return (
      <ClientLayout>
        <Page title="📋 Image Queue">
          <div className="flex justify-center items-center h-64">
            <Spinner accessibilityLabel="Loading images" size="large" />
          </div>
        </Page>
      </ClientLayout>
    );
  }

  return (
    <ClientLayout>
      <Frame>
        <Page title="📋 Image Queue">
          {images.length === 0 ? (
            <EmptyState
              heading="No images in the queue"
              image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/empty-state.svg"
            >
              <p>Upload images to start processing them with AI.</p>
            </EmptyState>
          ) : (
            <Grid columns={{ xs: 1, sm: 2, md: 3 }}>
              {images.map((img) => (
                <Box key={img.id} padding="300">
                  <Card>
                    <BlockStack gap="200">
                      <Text variant="headingSm" as="h3">
                        {getStatusBadge(img.status)}
                      </Text>

                      <BlockStack gap="100">
                        <div>
                          <Text as="p" tone="subdued">
                            Original Image:
                          </Text>
                          <Thumbnail
                            size="large"
                            source={img.image_url}
                            alt={`Original image ${img.id}`}
                          />
                        </div>

                        {['processed', 'completed'].includes(img.status) &&
                          img.processed_url && (
                            <div>
                              <Text as="p" tone="subdued">
                                Processed Image:
                              </Text>
                              <Thumbnail
                                size="large"
                                source={img.processed_url}
                                alt={`Processed image ${img.id}`}
                              />
                            </div>
                          )}

                        {['failed', 'error'].includes(img.status) && (
                          <Text tone="critical" as="p">
                            ⚠️ Error: {img.error_message || 'Unknown error'}
                          </Text>
                        )}
                      </BlockStack>
                    </BlockStack>
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
