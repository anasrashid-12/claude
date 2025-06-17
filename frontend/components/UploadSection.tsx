'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Image from 'next/image'; // ✅ Use Next.js Image

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
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
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

      const uploadRes = await axios.post<{ url: string }>(
        'http://localhost:8001/upload',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      const uploadedUrl = uploadRes.data?.url;
      if (!uploadedUrl) throw new Error('Image upload failed');

      const processRes = await axios.post<{ image_id: string }>(
        'http://localhost:8000/image/process',
        { image_url: uploadedUrl, shop }
      );

      setMessage(`✅ Image queued! ID: ${processRes.data.image_id}`);
      setFile(null);
      setPreviewUrl(null);
    } catch (err) {
      console.error('Upload error:', err);
      const message =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : 'Upload failed';
      setMessage(`❌ ${message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-xl font-semibold mb-4">Upload Image</h2>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="mb-4 block"
      />

      {previewUrl && (
        <div className="relative w-48 h-48 mb-4 border rounded overflow-hidden">
          <Image
            src={previewUrl}
            alt="Preview"
            layout="fill"
            objectFit="cover"
            className="rounded"
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
        <p className="mt-4 text-sm text-gray-700 whitespace-pre-line">
          {message}
        </p>
      )}
    </div>
  );
}