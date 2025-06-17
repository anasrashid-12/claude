// frontend/components/ImageCard.tsx
import Image from "next/image";

interface ImageData {
  id: string;
  image_url: string;
  status: string;
  processed_url?: string;
  error_message?: string;
}

export default function ImageCard({ image }: { image: ImageData }) {
  return (
    <div className="border rounded-lg p-4 shadow-sm bg-white">
      <div className="relative w-full h-48 mb-2">
        <Image
          src={image.image_url}
          alt={`Image ${image.id}`}
          layout="fill"
          objectFit="cover"
          className="rounded"
        />
      </div>
      <p className="text-sm text-gray-600">Status: {image.status}</p>
      {image.processed_url && (
        <a
          href={image.processed_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline text-sm"
        >
          View Processed
        </a>
      )}
      {image.error_message && (
        <p className="text-sm text-red-600">Error: {image.error_message}</p>
      )}
    </div>
  );
}