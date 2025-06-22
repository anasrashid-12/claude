// frontend/components/UploadSection.tsx
'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Image from 'next/image';

interface UploadSectionProps {
  shop: string;
}

export default function UploadSection({ shop }: UploadSectionProps) {
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
    if (!file || !shop) return;
    setUploading(true);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const { data: uploadData } = await axios.post<{ url: string }>(
        'http://localhost:8001/upload',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      const uploadedUrl = uploadData?.url;
      if (!uploadedUrl) throw new Error('Upload response missing URL');

      const { data: processData } = await axios.post<{ image_id: string }>(
        'http://localhost:8000/image/process',
        { image_url: uploadedUrl, shop }
      );

      setMessage(`✅ Image queued!\nID: ${processData.image_id}`);
      setFile(null);
      setPreviewUrl(null);
    } catch (err) {
      console.error('Upload error:', err);
      const detail =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Upload failed';
      setMessage(`❌ ${detail}`);
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
          <Image
            src={previewUrl}
            alt="Preview"
            fill
            className="object-cover rounded"
          />
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500 disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : 'Upload and Queue'}
      </button>

      {message && (
        <p className="text-sm text-gray-700 whitespace-pre-line">{message}</p>
      )}
    </div>
  );
}
