'use client';

import Image from 'next/image';
import { ImageData } from './ImageGallery';

export default function ImageCard({ image }: { image: ImageData }) {
  const canDownload = image.status === 'processed' && !!image.processed_url;

  const getStatusBadge = () => {
    const base = 'inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold';
    if (image.status === 'processed') return <span className={`${base} text-green-700 bg-green-100`}>✅ Done</span>;
    if (['processing', 'queued'].includes(image.status)) return <span className={`${base} text-yellow-700 bg-yellow-100`}>⏳ Processing</span>;
    if (['error', 'failed'].includes(image.status)) return <span className={`${base} text-red-700 bg-red-100`}>❌ Failed</span>;
    return <span className={`${base} text-gray-600 bg-gray-100`}>{image.status}</span>;
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm hover:shadow-md transition-shadow p-4 space-y-3 group">
      <div className="relative w-full h-40 sm:h-48 md:h-56 rounded-lg overflow-hidden bg-gray-100">
        <Image
          src={image.processed_url || image.image_url}
          alt={`Image (${image.status})`}
          fill
          sizes="(max-width: 768px) 100vw, 33vw"
          className="object-cover group-hover:scale-105 transition-transform"
        />
      </div>

      <div className="text-xs sm:text-sm space-y-2">
        <p className="text-gray-600">Status: {getStatusBadge()}</p>

        {canDownload && (
          <div className="flex flex-wrap items-center gap-2">
            <a href={image.processed_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline font-medium">
              🔍 View
            </a>
            <a href={image.processed_url} download className="text-xs bg-gray-100 border border-gray-300 rounded-md px-2 py-1 text-gray-700 hover:bg-gray-200">
              ⬇️ Download
            </a>
          </div>
        )}

        {image.error_message && <p className="text-xs text-red-500">⚠️ {image.error_message}</p>}
      </div>
    </div>
  );
}
