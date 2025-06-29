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
  shop: string; // ✅ Add this field
}

export default function ImageGallery({ shop }: { shop: string }) {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchImages = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images`
      );

      if (!res.ok) {
        throw new Error('Failed to fetch images');
      }

      const data = await res.json();

      const filteredImages = data.filter(
        (img: ImageData) => img.shop === shop
      );

      setImages(filteredImages);
    } catch (err) {
      console.error('Error fetching images:', err);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (shop) {
      fetchImages();
    }
  }, [shop]);

  if (loading) {
    return <p className="p-4 text-gray-500">Loading images...</p>;
  }

  if (error) {
    return (
      <p className="p-4 text-red-500">
        ❌ Failed to load images. Please try again later.
      </p>
    );
  }

  if (images.length === 0) {
    return (
      <p className="p-4 text-gray-500">
        No images found. Upload some to get started.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {images.map((image) => (
        <ImageCard key={image.id} image={image} />
      ))}
    </div>
  );
}
