'use client';

import { useState } from 'react';
import axios from 'axios';

interface UploadSectionProps {
  shop: string;
}

export default function UploadSection({ shop }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

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
      // Upload image to a temporary public hosting service or Supabase bucket
      const formData = new FormData();
      formData.append('file', file);

      const uploadRes = await axios.post('http://localhost:8001/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const uploadedUrl = uploadRes.data.url;
      if (!uploadedUrl) throw new Error('Image upload failed');

      // Send image URL to backend queue
      const processRes = await axios.post('http://localhost:8000/image/process', {
        image_url: uploadedUrl,
        shop,
      });

      setMessage(`Image queued successfully! ID: ${processRes.data.image_id}`);
      setFile(null);
      setPreviewUrl(null);
    } catch (err: any) {
      console.error('Upload error:', err);
      setMessage(`Error: ${err?.response?.data?.detail || 'Upload failed'}`);
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
        <img
          src={previewUrl}
          alt="Preview"
          className="w-48 h-48 object-cover rounded mb-4 border"
        />
      )}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500 disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : 'Upload and Queue'}
      </button>

      {message && <p className="mt-4 text-sm text-gray-700">{message}</p>}
    </div>
  );
}
