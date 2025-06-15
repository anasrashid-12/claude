'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

interface ImageData {
  id: string;
  image_url: string;
  processed_url: string | null;
  status: string;
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
        const res = await axios.get('http://localhost:8000/image/supabase/get-images', {
          params: { shop },
        });
        setImages(res.data.images || []);
      } catch (error) {
        console.error('Error fetching images:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [shop]);

  if (loading) {
    return <p className="text-center text-gray-500">Loading images...</p>;
  }

  if (!images.length) {
    return <p className="text-center text-gray-500">No images found for this shop.</p>;
  }

  return (
    <div className="mt-10">
      <h2 className="text-xl font-semibold mb-4">Image Gallery</h2>
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {images.map((img) => (
          <div key={img.id} className="bg-white shadow rounded p-4">
            <img
              src={img.image_url}
              alt="Original"
              className="w-full h-40 object-cover rounded mb-2"
            />
            <div className="text-sm text-gray-600">
              <p><strong>Status:</strong> {img.status}</p>
              {img.status === 'completed' && img.processed_url && (
                <div className="mt-2">
                  <p className="text-green-600 font-semibold">Processed:</p>
                  <img
                    src={img.processed_url}
                    alt="Processed"
                    className="w-full h-32 object-cover rounded border mt-1"
                  />
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
