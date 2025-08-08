'use client';

import { useEffect, useState } from 'react';
import useSWR from 'swr';
import useShop from '@/hooks/useShop';
import Image from 'next/image';
import Link from 'next/link';
import { RefreshCw } from 'lucide-react';
import { getSupabase } from '../../../../utils/supabase/supabaseClient';

interface ImageItem {
  id: string;
  original_path: string;
  processed_path?: string;
  status: 'pending' | 'processing' | 'processed' | 'completed' | 'failed' | 'queued';
  error_message?: string;
  filename: string;
}

const fetcher = (url: string) =>
  fetch(url, { credentials: 'include' }).then((res) => res.json());

export default function GalleryPage() {
  const { shop, loading: shopLoading } = useShop();
  const supabase = getSupabase();
  const { data, error, isLoading, mutate } = useSWR(
    shop ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/images` : null,
    fetcher,
    { refreshInterval: 5000 }
  );

  const [signedUrls, setSignedUrls] = useState<Record<string, string>>({});

  // fetch signed URLs for processed images
  useEffect(() => {
    const fetchSignedUrls = async () => {
      if (!data?.images) return;

      const paths = data.images
        .filter((img: ImageItem) => img.processed_path && !signedUrls[img.processed_path])
        .map((img: ImageItem) => img.processed_path!);

      const updates: Record<string, string> = {};

      await Promise.all(
        paths.map(async (path: string) => {
          try {
            const res = await fetch(
              `${process.env.NEXT_PUBLIC_BACKEND_URL}/fileserve/signed-url/${encodeURIComponent(path)}`,
              { credentials: 'include' }
            );
            const json = await res.json();
            if (res.ok && json.signed_url) {
              updates[path] = json.signed_url;
            }
          } catch (err) {
            console.warn(`Failed to fetch signed URL for ${path}`);
          }
        })
      );

      if (Object.keys(updates).length > 0) {
        setSignedUrls((prev) => ({ ...prev, ...updates }));
      }
    };

    fetchSignedUrls();
  }, [data?.images, signedUrls]);

  // subscribe to real-time updates from Supabase
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
  }, [shop, mutate, supabase]);

  const handleDownload = (path: string) => {
    if (!path) return;
    const url = `${process.env.NEXT_PUBLIC_BACKEND_URL}/fileserve/download?path=${encodeURIComponent(path)}`;
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', path.split('/').pop() ?? 'image.png');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (shopLoading || isLoading) {
    return <div className="p-6 text-center text-gray-500">Loading...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">Error loading images.</div>;
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
        </div>
      ) : (
        <div className="mt-6 max-h-[600px] overflow-y-auto pr-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {processedImages.map((img) => {
              const previewUrl = img.processed_path ? signedUrls[img.processed_path] : '';

              return (
                <Link key={img.id} href={previewUrl || '#'} target="_blank">
                  <div className="rounded-xl border bg-white dark:bg-[#1e293b] p-4 shadow hover:scale-[1.02] transition-transform">
                    <div className="relative w-full h-48 rounded overflow-hidden mb-3">
                      {previewUrl ? (
                        <Image
                          src={previewUrl}
                          alt={img.filename}
                          fill
                          className="object-cover"
                          unoptimized
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-sm text-gray-400">
                          Preview unavailable
                        </div>
                      )}
                    </div>
                    <div className="text-sm space-y-1">
                      <p>Status: <span className="text-green-600 font-medium">✅ Done</span></p>
                      <button
                        onClick={(e) => {
                          e.preventDefault();
                          handleDownload(img.processed_path || img.original_path);
                        }}
                        className="text-blue-500 hover:underline font-medium"
                      >
                        ⬇️ Download Image
                      </button>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
