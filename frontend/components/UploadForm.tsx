'use client';

import { useState, FormEvent } from 'react';
import { queueImage } from '../utils/api';

interface UploadFormProps {
  shop: string;
  onUpload: () => void;
}

export default function UploadForm({ shop, onUpload }: UploadFormProps) {
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    if (!imageUrl || !imageUrl.startsWith('http')) {
      setError('Please enter a valid image URL.');
      return;
    }

    try {
      const res = await queueImage(imageUrl, shop);
      if (res?.success) {
        setImageUrl('');
        onUpload();
      } else {
        setError('Upload failed. Please try again.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('Something went wrong.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input
        type="url"
        value={imageUrl}
        onChange={(e) => setImageUrl(e.target.value)}
        placeholder="Enter image URL"
        className="border p-3 rounded w-full"
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        type="submit"
        className="bg-black text-white py-2 px-4 rounded hover:bg-gray-800 transition"
      >
        Upload and Queue
      </button>
    </form>
  );
}