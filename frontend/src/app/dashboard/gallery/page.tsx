'use client';

import { useEffect, useState } from 'react';
import useShop from '@/hooks/useShop';
import { createClient } from '@supabase/supabase-js';
import Image from 'next/image';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

interface ImageItem {
  id: string;
  image_url: string;
  processed_url?: string;
  status: string;
  error_message?: string;
}

export default function GalleryPage() {
  const { shop, loading: shopLoading } = useShop();
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchImages = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`,
        { credentials: 'include' }
      );
      const data = await res.json();
      setImages(data.images || []);
    } catch (err) {
      console.error('Error fetching gallery images:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!shop) return;

    fetchImages();

    const channel = supabase
      .channel(`realtime:gallery-${shop}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'images',
          filter: `shop=eq.${shop}`,
        },
        (payload) => {
          const newRecord = payload.new as ImageItem;
          const eventType = payload.eventType;

          if (eventType === 'INSERT') {
            setImages((prev) => [newRecord, ...prev]);
          } else if (eventType === 'UPDATE') {
            setImages((prev) =>
              prev.map((img) => (img.id === newRecord.id ? newRecord : img))
            );
          } else if (eventType === 'DELETE') {
            const deletedId = (payload.old as ImageItem).id;
            setImages((prev) => prev.filter((img) => img.id !== deletedId));
          }
        }
      )
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, [shop]);

  if (shopLoading || loading) {
    return <p className="text-center mt-10 text-gray-500">Loading gallery...</p>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">🖼️ Processed Gallery</h1>

      {images.length === 0 ? (
        <p className="text-center text-gray-500">No processed images found yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {images.map((img) => (
            <div
              key={img.id}
              className="rounded-xl border border-gray-200 bg-white p-3 shadow hover:shadow-md transition-shadow"
            >
              <div className="relative w-full h-48 rounded overflow-hidden">
                <Image
                  src={img.processed_url || img.image_url}
                  alt={`Image ${img.id}`}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 33vw"
                />
              </div>

              <div className="mt-3 text-sm space-y-1">
                <p className="text-gray-600">
                  Status:{' '}
                  {img.status === 'processed' ? (
                    <span className="text-green-600 font-medium">✅ Done</span>
                  ) : ['queued', 'processing'].includes(img.status) ? (
                    <span className="text-yellow-600 font-medium">🕒 Processing</span>
                  ) : ['error', 'failed'].includes(img.status) ? (
                    <span className="text-red-600 font-medium">❌ Failed</span>
                  ) : (
                    <span className="text-gray-600 font-medium">{img.status}</span>
                  )}
                </p>

                {img.error_message && (
                  <p className="text-xs text-red-500">⚠️ {img.error_message}</p>
                )}

                {img.processed_url && (
                  <a
                    href={img.processed_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    🔍 View Full Image
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
