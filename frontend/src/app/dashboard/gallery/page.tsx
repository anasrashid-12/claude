'use client';

import { useEffect, useState } from 'react';
import useShop from '@/hooks/useShop';
import Image from 'next/image';

interface ImageItem {
  id: string;
  status: 'queued' | 'processing' | 'processed' | 'failed' | string;
  image_url: string;
  processed_url?: string;
  error_message?: string;
}

export default function GalleryPage() {
  const { shop, loading: shopLoading } = useShop();
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(true);

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
        console.error('Error fetching images:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [shop]);

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processed':
        return <span className="text-green-600">✅ Done</span>;
      case 'queued':
      case 'pending':
      case 'processing':
        return <span className="text-yellow-600">🕒 Processing</span>;
      case 'failed':
        return <span className="text-red-600">❌ Failed</span>;
      default:
        return <span className="text-gray-600">Unknown</span>;
    }
  };

  if (shopLoading || loading) {
    return <p className="text-gray-500 text-center mt-10">Loading...</p>;
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">📸 Processed Gallery</h1>

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
                <p>Status: {getStatusLabel(img.status)}</p>
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
