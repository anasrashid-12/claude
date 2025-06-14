'use client';

import {
  Page,
  Layout,
  Card,
  Thumbnail,
  Text,
  Badge,
  Grid,
  Spinner,
  Frame,
} from '@shopify/polaris';
import { useEffect, useState } from 'react';
import { useAuthenticatedFetch } from '../hooks/useAuthenticatedFetch';

interface ImageItem {
  id: string;
  product_id: string;
  original_url: string;
  processed_url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export default function ImageGallery() {
  const fetch = useAuthenticatedFetch();
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/v1/image-gallery');
        const data = await res?.json();
        setImages(data.images || []);
      } catch (error) {
        console.error('Failed to load gallery:', error);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [fetch]);

  if (loading) {
    return (
      <Frame>
        <Page title="Image Gallery">
          <Card>
            <div style={{ padding: 24, textAlign: 'center' }}>
              <Spinner size="large" />
            </div>
          </Card>
        </Page>
      </Frame>
    );
  }

  return (
    <Page title="Image Gallery">
      <Layout>
        <Layout.Section>
          <Grid columns={{ xs: 1, sm: 2, md: 3, lg: 4 }}>
            {images.map((image) => (
              <Card key={image.id} padding="400">
                <Text as="h6" variant="bodyMd" fontWeight="bold">Product #{image.product_id}</Text>
                <Badge tone={image.status === 'completed' ? 'success' : 'warning'}>
                  {image.status}
                </Badge>
                <Thumbnail source={image.original_url} alt="Original Image" size="small" />
                <Thumbnail source={image.processed_url} alt="Processed Image" size="small" />
              </Card>
            ))}
          </Grid>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
