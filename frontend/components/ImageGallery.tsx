// frontend/components/ImageGallery.tsx
'use client';

import { useEffect, useState } from 'react';
import axios, { AxiosError } from 'axios';
import ImageCard, { ImageData } from './ImageCard';

interface Props {
  shop: string;
}

export default function ImageGallery({ shop }: Props) {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shop) return;

    const fetchImages = async () => {
      try {
        const res = await axios.get<{ images: ImageData[] }>(
          'http://localhost:8000/image/supabase/get-images',
          { params: { shop } }
        );
        setImages(res.data.images || []);
      } catch (err) {
        const axiosError = err as AxiosError;
        setError(axiosError.message);
        console.error('Fetch error:', axiosError);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [shop]);

  if (loading) {
    return <p className="text-center text-gray-500">Loading images...</p>;
  }

  if (error) {
    return <p className="text-center text-red-600">Failed to load images: {error}</p>;
  }

  if (images.length === 0) {
    return <p className="text-center text-gray-500">No images found for this shop.</p>;
  }

  return (
    <div className="mt-10">
      <h2 className="text-xl font-semibold mb-4">Image Gallery</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {images.map((img) => (
          <ImageCard key={img.id} image={img} />
        ))}
      </div>
    </div>
  );
}
