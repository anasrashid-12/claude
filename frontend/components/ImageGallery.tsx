'use client';

import { useEffect, useState } from 'react';
import ImageCard from './ImageCard';

export interface ImageData {
  id: string;
  image_url: string;
  status: string;
  processed_url?: string;
  error_message?: string;
}

interface ImageGalleryProps {
  shop: string;
}

export default function ImageGallery({ shop }: ImageGalleryProps) {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images`,
          { credentials: 'include' }
        );
        const data = await res.json();
        setImages(data.images || []);
      } catch (err) {
        console.error('Failed to fetch images:', err);
      } finally {
        setLoading(false);
      }
    };

    if (shop) fetchImages();
  }, [shop]);

  if (loading) {
    return <p className="text-center text-gray-500">Loading images...</p>;
  }

  if (images.length === 0) {
    return <p className="text-center text-gray-500">No images found.</p>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
      {images.map((img) => (
        <ImageCard key={img.id} image={img} />
      ))}
    </div>
  );
}
