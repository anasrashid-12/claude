'use client';

import { useEffect, useState } from 'react';
import ImageCard from './ImageCard';
import { RefreshCw } from 'lucide-react';

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
  const [refreshing, setRefreshing] = useState(false);

  const fetchImages = async () => {
    setRefreshing(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`,
        { credentials: 'include' }
      );
      if (!res.ok) throw new Error('Failed to fetch images');
      const data = await res.json();
      setImages(data.images || []);
    } catch (err) {
      console.error(err);
      setError(true);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (shop) fetchImages();
  }, [shop]);

  if (loading) return <p className="text-center py-12 text-gray-500">🔄 Loading images...</p>;
  if (error) return <p className="text-center py-12 text-red-600">❌ Failed to load images.</p>;
  if (images.length === 0)
    return <p className="text-center py-12 text-gray-500">📭 No images yet.</p>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-center gap-2">
        <h2 className="text-xl font-semibold text-gray-800">📸 Your Processed Images</h2>
        <button
          onClick={fetchImages}
          disabled={refreshing}
          className="flex items-center gap-1 text-sm text-blue-600 hover:underline disabled:opacity-50"
        >
          {refreshing && <RefreshCw className="w-4 h-4 animate-spin" />}
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {images.map((img) => (
          <ImageCard key={img.id} image={img} />
        ))}
      </div>
    </div>
  );
}
