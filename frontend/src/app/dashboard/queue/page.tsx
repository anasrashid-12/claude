'use client';

import useShop from '@/hooks/useShop';
import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';
import { Badge, EmptyState, Thumbnail, BlockStack, Text } from '@shopify/polaris';

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

  useEffect(() => {
    if (!shop) return;

    let interval: NodeJS.Timeout;
    let channel: ReturnType<typeof supabase.channel>;

    const fetchImages = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/images`, {
          credentials: 'include',
        });
        const data = await res.json();
        setImages(data.images || []);
      } catch (err) {
        console.error('❌ Error fetching images:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
    interval = setInterval(fetchImages, 10000); // poll every 10s

    channel = supabase
      .channel(`realtime:images-${shop}`)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'images', filter: `shop=eq.${shop}` },
        (payload) => {
          const newRecord = payload.new as ImageRecord;
          const eventType = payload.eventType;
          setImages((prev) => {
            if (eventType === 'INSERT') return [newRecord, ...prev];
            if (eventType === 'UPDATE')
              return prev.map((img) => (img.id === newRecord.id ? newRecord : img));
            if (eventType === 'DELETE')
              return prev.filter((img) => img.id !== (payload.old as ImageRecord).id);
            return prev;
          });
        }
      )
      .subscribe();

    return () => {
      clearInterval(interval);
      supabase.removeChannel(channel);
    };
  }, [shop]);

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'queued':
        return <Badge tone="info">Queued</Badge>;
      case 'processing':
        return <Badge tone="attention">Processing</Badge>;
      case 'processed':
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
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 p-6 animate-pulse">
        {Array.from({ length: 6 }).map((_, idx) => (
          <div key={idx} className="rounded-xl border bg-gray-100 dark:bg-gray-800 p-4 shadow">
            <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-1/4 mb-4" />
            <div className="w-full h-32 bg-gray-300 dark:bg-gray-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  const activeImages = images.filter((img) => ['queued', 'processing'].includes(img.status));

  return (
    <div className="px-4 sm:px-6 pt-10 pb-16 max-w-7xl mx-auto text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">📋 Image Queue</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">Monitor your image processing queue in real time.</p>

      {activeImages.length === 0 ? (
        <EmptyState
          heading="No images in the queue"
          image="https://cdn.shopify.com/s/files/1/0262/4071/2726/files/empty-state.svg"
        >
          <p>Upload images to start processing them with AI.</p>
        </EmptyState>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {activeImages.map((img) => (
            <div
              key={img.id}
              className="rounded-xl border bg-white dark:bg-[#1e293b] p-4 shadow hover:scale-[1.02] transition-transform"
            >
              <BlockStack gap="200">
                <Text variant="headingSm" as="h3">{getStatusBadge(img.status)}</Text>
                <BlockStack gap="100">
                  <div>
                    <Text as="p" tone="subdued">Original Image:</Text>
                    <Thumbnail size="large" source={img.image_url} alt={`Original ${img.id}`} />
                  </div>
                  {['failed', 'error'].includes(img.status) && (
                    <Text tone="critical" as="p">
                      ⚠️ Error: {img.error_message || 'Unknown error'}
                    </Text>
                  )}
                </BlockStack>
              </BlockStack>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
