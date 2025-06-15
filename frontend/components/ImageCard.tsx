// frontend/components/ImageCard.tsx
export default function ImageCard({ image }: { image: any }) {
    return (
      <div className="border rounded-lg p-4 shadow-sm bg-white">
        <img src={image.image_url} alt="Original" className="w-full rounded mb-2" />
        <p className="text-sm text-gray-600">Status: {image.status}</p>
        {image.processed_url && (
          <a href={image.processed_url} target="_blank" rel="noopener noreferrer" className="text-blue-600">
            View Processed
          </a>
        )}
        {image.error_message && (
          <p className="text-sm text-red-600">Error: {image.error_message}</p>
        )}
      </div>
    );
  }
  