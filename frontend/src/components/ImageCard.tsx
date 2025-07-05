'use client';

import Image from 'next/image';
import { ImageData } from './ImageGallery';

export default function ImageCard({ image }: { image: ImageData }) {
  const canDownload = image.status === 'processed' && image.processed_url;

  return (
    <div className="rounded-2xl border border-gray-200 bg-white shadow-sm hover:shadow-lg transition-shadow duration-200 p-4 space-y-4 group">
      {/* Image Preview */}
      <div className="relative w-full h-48 rounded-lg overflow-hidden bg-gray-100">
        <Image
          src={image.processed_url || image.image_url}
          alt={`Image ${image.id}`}
          fill
          sizes="(max-width: 768px) 100vw, 33vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
        />
      </div>

      {/* Status + Actions */}
      <div className="text-sm space-y-2">
        {/* Status Badge */}
        <p className="text-gray-500">
          Status:{' '}
          {image.status === 'processed' ? (
            <span className="text-green-600 font-semibold bg-green-50 px-2 py-0.5 rounded-md">
              ✅ Done
            </span>
          ) : ['processing', 'queued'].includes(image.status) ? (
            <span className="text-yellow-600 font-semibold bg-yellow-50 px-2 py-0.5 rounded-md">
              🕒 Processing
            </span>
          ) : ['error', 'failed'].includes(image.status) ? (
            <span className="text-red-600 font-semibold bg-red-50 px-2 py-0.5 rounded-md">
              ❌ Failed
            </span>
          ) : (
            <span className="text-gray-600 font-medium">{image.status}</span>
          )}
        </p>

        {/* Actions */}
        {canDownload && (
          <div className="flex gap-4 items-center mt-2">
            <a
              href={image.processed_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline font-medium"
            >
              🔍 View
            </a>
            <a
              href={image.processed_url}
              download
              className="text-xs bg-gray-100 border border-gray-300 rounded-md px-3 py-1 text-gray-700 hover:bg-gray-200 transition"
            >
              ⬇️ Download
            </a>
          </div>
        )}

        {/* Error */}
        {image.error_message && (
          <p className="text-xs text-red-500 mt-1">
            ⚠️ {image.error_message}
          </p>
        )}
      </div>
    </div>
  );
}
