'use client';

import { useState } from 'react';
import useShop from '@/hooks/useShop';

export default function UploadPage() {
  const { shop, loading: shopLoading } = useShop();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleUpload = async () => {
    if (!file || !shop) return;

    setLoading(true);
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('image', file);

      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();

      const imageUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/${uploadData.filename}`;

      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl, shop }),
      });

      const result = await processRes.json();
      if (result.success) {
        setMessage('✅ Image queued for processing!');
        setFile(null);
      } else {
        setMessage('❌ Failed to process image.');
      }
    } catch {
      setMessage('❌ Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  if (shopLoading) {
    return <p className="text-gray-500 text-center mt-10">Loading...</p>;
  }

  return (
    <div className="max-w-xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Upload Image</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mb-4"
      />

      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="px-4 py-2 bg-black text-white rounded-xl hover:bg-gray-800 disabled:opacity-50"
      >
        {loading ? 'Uploading...' : 'Upload & Queue'}
      </button>

      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  );
}
