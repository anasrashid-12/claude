'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import useShop from '@/hooks/useShop';

export default function UploadSection() {
  const { shop, loading: shopLoading } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);

  // Previews
  useEffect(() => {
    const urls = files.map((file) => URL.createObjectURL(file));
    setPreviews(urls);
    return () => urls.forEach((url) => URL.revokeObjectURL(url));
  }, [files]);

  // File input change
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...selected]);
    setMessages([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Drag & drop
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'));
    setFiles((prev) => [...prev, ...dropped]);
    setMessages([]);
  };

  // Upload
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
        console.error(error);
        newMessages.push(`❌ ${file.name} failed`);
      }
    }

    setMessages(newMessages);
    setUploading(false);
    setFiles([]);
    setPreviews([]);
  };

  if (shopLoading) return <p className="text-gray-500 mt-10">Loading shop...</p>;

  return (
    <div className="bg-white p-6 rounded-2xl shadow space-y-6 border border-gray-100">
      {/* Header */}
      <h2 className="text-xl font-semibold text-gray-800">📤 Upload Images</h2>

      {/* Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className="w-full border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition"
      >
        <input
          type="file"
          accept="image/*"
          multiple
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        <p className="text-sm text-gray-500">Click or drag & drop image(s) here</p>
      </div>

      {/* Previews */}
      {previews.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {previews.map((src, idx) => (
            <div
              key={idx}
              className="relative w-full h-40 rounded-lg overflow-hidden bg-gray-100 shadow-sm"
            >
              <Image src={src} alt={`Preview ${idx}`} fill className="object-cover" />
            </div>
          ))}
        </div>
      )}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={!files.length || uploading}
        className="w-full sm:w-auto bg-black text-white px-5 py-2.5 rounded-lg hover:bg-gray-800 disabled:opacity-50 transition"
      >
        {uploading ? 'Uploading...' : `Upload ${files.length} Image${files.length > 1 ? 's' : ''}`}
      </button>

      {/* Messages */}
      {messages.length > 0 && (
        <div className="space-y-1 text-sm">
          {messages.map((msg, idx) => (
            <p key={idx} className={msg.startsWith('✅') ? 'text-green-600' : 'text-red-600'}>
              {msg}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
