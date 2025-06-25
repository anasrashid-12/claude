'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';

export default function UploadSection() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setPreviewUrl(URL.createObjectURL(selected));
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('image', file);

      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!uploadRes.ok) throw new Error('Upload failed');

      const data = await uploadRes.json();
      setMessage(`✅ Image uploaded & queued.\nID: ${data.image_id}`);
      setFile(null);
      setPreviewUrl(null);
    } catch (err) {
      console.error('Upload error:', err);
      setMessage('❌ Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-4">
      <h2 className="text-xl font-semibold">Upload Image</h2>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="block w-full border border-gray-300 rounded p-2"
      />

      {previewUrl && (
        <div className="relative w-48 h-48 border rounded overflow-hidden">
          <Image src={previewUrl} alt="Preview" fill className="object-cover rounded" />
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : 'Upload & Queue'}
      </button>

      {message && <p className="text-sm text-gray-700 whitespace-pre-line">{message}</p>}
    </div>
  );
}
