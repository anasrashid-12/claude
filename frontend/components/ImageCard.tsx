'use client';

import Image from 'next/image';

export interface ImageData {
  id: string;
  image_url: string;
  status: string;
  processed_url?: string;
  error_message?: string;
}

export default function ImageCard({ image }: { image: ImageData }) {
  return (
    <div className="border rounded-lg p-4 shadow bg-white space-y-2">
      <div className="relative w-full h-48">
        <Image
          src={image.image_url}
          alt={`Image ${image.id}`}
          fill
          className="rounded object-cover"
        />
      </div>

      <p className="text-sm text-gray-600">Status: {image.status}</p>

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
