'use client';

import { useState } from 'react';
import useShop from '@/hooks/useShop';

export default function UploadPage() {
  const { shop, loading: shopLoading } = useShop();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file || !shop) return;

    setLoading(true);
    setMessage('');
    setUploadedUrl(null);

    try {
      const formData = new FormData();
      formData.append('image', file);

      // 1. Upload to backend
      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include', // Required for JWT session cookie
      });

      if (!uploadRes.ok) throw new Error('Upload failed');
      const uploadData = await uploadRes.json();
      const imageUrl = uploadData.url;

      // 2. Send to processing queue
      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl, shop }),
      });

      const processData = await processRes.json();
      if (!processRes.ok || !processData.success) {
        console.error('Queue failed:', processData);
        throw new Error('Processing queue failed');
      }

      setMessage('✅ Image uploaded and queued for processing!');
      setUploadedUrl(imageUrl);
      setFile(null);
    } catch (error) {
      console.error(error);
      setMessage('❌ Something went wrong during upload or processing.');
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

      {uploadedUrl && (
        <div className="mt-4">
          <p className="text-sm text-gray-600">📸 Uploaded Image:</p>
          <img src={uploadedUrl} alt="Uploaded" className="mt-2 rounded-lg shadow-md" />
        </div>
      )}
    </div>
  );
}
