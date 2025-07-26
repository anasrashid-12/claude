'use client';

import useSWR from 'swr';
import useShop from '@/hooks/useShop';
import { useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { RefreshCw } from 'lucide-react';
import { getSupabase } from '../../../../utils/supabaseClient'; // ✅ Using shared client

interface ImageItem {
  id: string;
  image_url: string;
  processed_url?: string;
  status: string;
  error_message?: string;
  filename: string;
}

const fetcher = (url: string) =>
  fetch(url, { credentials: 'include' }).then((res) => res.json());

export default function GalleryPage() {
  const { shop, loading: shopLoading } = useShop();
  const supabase = getSupabase(); // ✅ Reuse shared instance

  const { data, error, isLoading, mutate } = useSWR(
    shop ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/images` : null,
    fetcher,
    { refreshInterval: 5000 }
  );

  useEffect(() => {
    if (!shop) return;

    const channel = supabase
      .channel(`realtime:gallery-${shop}`)
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'images',
          filter: `shop=eq.${shop}`,
        },
        () => mutate()
      )
      .subscribe();

    return () => {
      void supabase.removeChannel(channel);
    };
  }, [shop, mutate, supabase]); // ✅ include supabase in deps

  const handleDownload = (filename: string) => {
    const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/fileserve/download?filename=${encodeURIComponent(filename)}`;
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename.split('/').pop()!);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (shopLoading || isLoading) {
    return <div className="p-6 text-center text-gray-500">⏳ Loading processed images...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">❌ Failed to load images.</div>;
  }

  const images: ImageItem[] = data?.images || [];
  const processedImages = images.filter((img) => img.status === 'processed');

  return (
    <div className="px-4 sm:px-6 pt-10 pb-16 max-w-7xl mx-auto text-gray-900 dark:text-white">
      <div className="flex justify-between items-center sticky top-0 bg-white dark:bg-[#1e293b] rounded-xl p-4 shadow mb-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">🖼️ Processed Gallery</h1>
          <p className="text-gray-600 dark:text-gray-400">Browse your AI-processed images below.</p>
        </div>
        <button onClick={() => mutate()} className="flex items-center gap-1 text-blue-500 hover:underline">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {processedImages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-center text-gray-500 dark:text-gray-400 mt-6">
          <p className="text-lg font-medium">No processed images yet.</p>
          <p className="text-sm mt-1">
            Upload images from the <strong>Upload</strong> tab and check back later.
          </p>
        </div>
      ) : (
        <div className="mt-6 max-h-[600px] overflow-y-auto pr-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {processedImages.map((img: ImageItem) => (
              <Link key={img.id} href={img.processed_url || img.image_url} target="_blank">
                <div className="rounded-xl border bg-white dark:bg-[#1e293b] p-4 shadow hover:scale-[1.02] transition-transform">
                  <div className="relative w-full h-48 rounded overflow-hidden mb-3">
                    <Image
                      src={img.processed_url || img.image_url}
                      alt={`Processed Image ${img.id}`}
                      fill
                      className="object-cover"
                      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                      priority
                      unoptimized
                    />
                  </div>
                  <div className="text-sm space-y-1">
                    <p>Status: <span className="text-green-600 font-medium">✅ Done</span></p>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        handleDownload(img.filename);
                      }}
                      className="text-blue-500 hover:underline font-medium"
                    >
                      ⬇️ Download Image
                    </button>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
