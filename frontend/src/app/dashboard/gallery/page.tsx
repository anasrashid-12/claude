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
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`,
      { credentials: 'include' }
    );
    const data = await res.json();
    setImages(data.images || []);
    setLoading(false);
  };

  useEffect(() => {
    if (!shop) return;
    fetchImages();

    const channel = supabase
      .channel(`realtime:gallery-${shop}`)
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'images', filter: `shop=eq.${shop}` },
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
    return <p className="text-center mt-10">Loading...</p>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">🖼️ Processed Gallery</h1>

      {images.length === 0 ? (
        <p className="text-center text-gray-500">No images found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {images.map((img) => (
            <div key={img.id} className="border rounded-xl p-3 shadow bg-white">
              <div className="relative w-full h-48 rounded overflow-hidden">
                <Image
                  src={img.processed_url || img.image_url}
                  alt={`Image ${img.id}`}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="mt-3 text-sm">
                <p>
                  Status:{' '}
                  {img.status === 'processed' ? (
                    <span className="text-green-600">✅ Done</span>
                  ) : img.status === 'processing' || img.status === 'queued' ? (
                    <span className="text-yellow-600">🕒 Processing</span>
                  ) : img.status === 'error' || img.status === 'failed' ? (
                    <span className="text-red-600">❌ Failed</span>
                  ) : (
                    <span className="text-gray-600">{img.status}</span>
                  )}
                </p>
                {img.error_message && (
                  <p className="text-xs text-red-500 mt-1">{img.error_message}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
