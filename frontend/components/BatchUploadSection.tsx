'use client';

import { useState, useEffect, useRef } from 'react';
import useShop from '@/hooks/useShop';
import Image from 'next/image';

export default function BatchUploadSection() {
  const { shop, loading: shopLoading } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    if (files.length > 0) {
      const urls = files.map((file) => URL.createObjectURL(file));
      setPreviews(urls);
      return () => urls.forEach((url) => URL.revokeObjectURL(url));
    }
  }, [files]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    setFiles(selected);
    setMessages([]);
  };

  const handleUpload = async () => {
    if (!files.length || !shop) return;

    setUploading(true);
    const newMessages: string[] = [];

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('image', file);

        const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        if (!uploadRes.ok) throw new Error('Upload failed');
        const uploadData = await uploadRes.json();
        const imageUrl = uploadData.url;

        const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_url: imageUrl }),
        });

        if (!processRes.ok) throw new Error('Queue failed');

        newMessages.push(`✅ ${file.name} uploaded & queued`);
      } catch (error) {
        newMessages.push(`❌ ${file.name} failed`);
      }
    }

    setMessages(newMessages);
    setUploading(false);
    setFiles([]);
    setPreviews([]);
  };

  if (shopLoading) {
    return <p className="text-gray-500 text-center mt-10">Loading...</p>;
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-4">
      <h2 className="text-xl font-semibold">Batch Upload Images</h2>

      <input
        type="file"
        multiple
        accept="image/*"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="block w-full border border-gray-300 rounded p-2"
      />

      {previews.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {previews.map((src, idx) => (
            <div key={idx} className="relative w-full h-40 border rounded overflow-hidden">
              <Image src={src} alt={`Preview ${idx}`} fill className="object-cover" />
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!files.length || uploading}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500 disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : `Upload ${files.length} Images`}
      </button>

      {messages.length > 0 && (
        <div className="space-y-1 text-sm">
          {messages.map((msg, idx) => (
            <p key={idx}>{msg}</p>
          ))}
        </div>
      )}
    </div>
  );
}
