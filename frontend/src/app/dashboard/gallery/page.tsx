'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';

interface ImageItem {
  id: string;
  status: 'queued' | 'processed' | 'failed' | string;
  image_url: string;
  processed_url?: string;
  error_message?: string;
}

export default function GalleryPage() {
  const [images, setImages] = useState<ImageItem[]>([]);
  const [loading, setLoading] = useState(true);

  const shop = 'ai-image-app-dev-store.myshopify.com'; // TODO: Replace dynamically from session/context

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/supabase/get-images?shop=${shop}`
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
  }, []);

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processed':
        return <span className="text-green-600">✅ Done</span>;
      case 'queued':
        return <span className="text-yellow-600">🕒 Queued</span>;
      case 'failed':
        return <span className="text-red-600">❌ Failed</span>;
      default:
        return <span className="text-gray-600">Unknown</span>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold mb-6">📸 Processed Gallery</h1>

      {loading ? (
        <p className="text-gray-500 text-center">Loading...</p>
      ) : images.length === 0 ? (
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