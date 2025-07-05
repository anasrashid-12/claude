'use client';

import { useEffect, useState } from 'react';
import ImageCard from './ImageCard';

export interface ImageData {
  id: string;
  image_url: string;
  processed_url: string;
  status: string;
  created_at: string;
  error_message?: string;
  shop: string;
}

export default function ImageGallery({ shop }: { shop: string }) {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchImages = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`,
        { credentials: 'include' }
      );
      if (!res.ok) throw new Error('Failed to fetch images');

      const data = await res.json();
      setImages(data.images || []);
    } catch (err) {
      console.error('Error fetching images:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (shop) fetchImages();
  }, [shop]);

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-500 text-sm">
        🔄 Loading your images...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-600 text-sm">
        ❌ Failed to load images. Please try again later.
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 text-sm">
        📭 No images found. Upload some to get started.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
        <h2 className="text-xl font-semibold text-gray-800">📸 Your Processed Images</h2>
        <div className="flex items-center gap-3">
          <p className="text-sm text-gray-500">{images.length} image(s)</p>
          <button
            onClick={fetchImages}
            className="text-sm text-blue-600 hover:underline"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {images.map((image) => (
          <ImageCard key={image.id} image={image} />
        ))}
      </div>
    </div>
  );
}
