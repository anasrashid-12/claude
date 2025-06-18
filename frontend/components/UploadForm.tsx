// frontend/components/UploadForm.tsx
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
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    if (!imageUrl.startsWith('http')) {
      setError('⚠️ Please enter a valid image URL.');
      setSubmitting(false);
      return;
    }

    try {
      const res = await queueImage(imageUrl, shop);
      if (res?.success) {
        setImageUrl('');
        onUpload();
      } else {
        setError('❌ Upload failed. Please try again.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError('❌ Something went wrong.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <input
        type="url"
        value={imageUrl}
        onChange={(e) => setImageUrl(e.target.value)}
        placeholder="Enter direct image URL"
        className="border border-gray-300 p-3 rounded w-full"
        required
      />
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        type="submit"
        disabled={submitting}
        className="bg-black text-white py-2 px-4 rounded hover:bg-gray-800 disabled:opacity-50"
      >
        {submitting ? 'Uploading...' : 'Upload and Queue'}
      </button>
    </form>
  );
}
