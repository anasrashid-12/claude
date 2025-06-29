'use client';

import Image from 'next/image';
import { ImageData } from './ImageGallery';

export default function ImageCard({ image }: { image: ImageData }) {
  return (
    <div className="border rounded-lg p-4 shadow bg-white space-y-2">
      <div className="relative w-full h-48">
      <Image
        src={image.processed_url || image.image_url}
        alt={`Image ${image.id}`}
        fill
        sizes="(max-width: 768px) 100vw, 33vw"
        className="rounded object-cover"
      />
      </div>

      <p className="text-sm text-gray-600">
        Status:{' '}
        {image.status === 'processed' ? (
          <span className="text-green-600">✅ Done</span>
        ) : ['processing', 'queued'].includes(image.status) ? (
          <span className="text-yellow-600">🕒 Processing</span>
        ) : ['error', 'failed'].includes(image.status) ? (
          <span className="text-red-600">❌ Failed</span>
        ) : (
          <span className="text-gray-600">{image.status}</span>
        )}
      </p>

      {image.processed_url && (
        <a
          href={image.processed_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:underline"
        >
          🔍 View Processed Image
        </a>
      )}

      {image.error_message && (
        <p className="text-sm text-red-600">⚠️ Error: {image.error_message}</p>
      )}
    </div>
  );
}
