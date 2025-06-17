'use client';

import { useEffect, useState } from 'react';
import axios, { AxiosError } from 'axios';
import Image from 'next/image';

interface ImageData {
  id: string;
  image_url: string;
  processed_url: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at?: string;
}

interface Props {
  shop: string;
}

export default function ImageGallery({ shop }: Props) {
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!shop) return;

    const fetchImages = async () => {
      try {
        const res = await axios.get<{ images: ImageData[] }>(
          'http://localhost:8000/image/supabase/get-images',
          { params: { shop } }
        );
        setImages(res.data.images || []);
      } catch (error) {
        const err = error as AxiosError;
        console.error('Error fetching images:', err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [shop]);

  if (loading) {
    return <p className="text-center text-gray-500">Loading images...</p>;
  }

  if (images.length === 0) {
    return <p className="text-center text-gray-500">No images found for this shop.</p>;
  }

  return (
    <div className="mt-10">
      <h2 className="text-xl font-semibold mb-4">Image Gallery</h2>
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {images.map((img) => (
          <div key={img.id} className="bg-white shadow rounded p-4">
            <div className="relative w-full h-40 mb-2">
              <Image
                src={img.image_url}
                alt={`Original image ${img.id}`}
                fill
                className="rounded object-cover"
              />
            </div>

            <div className="text-sm text-gray-600">
              <p><strong>Status:</strong> {img.status}</p>

              {img.status === 'completed' && img.processed_url && (
                <div className="mt-2">
                  <p className="text-green-600 font-semibold">Processed:</p>
                  <div className="relative w-full h-32 mt-1 border rounded">
                    <Image
                      src={img.processed_url}
                      alt={`Processed image ${img.id}`}
                      fill
                      className="rounded object-cover"
                    />
                  </div>
                </div>
              )}

              {img.status === 'failed' && (
                <p className="text-red-600 mt-2">Error: {img.error_message}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}