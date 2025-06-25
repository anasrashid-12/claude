'use client';

import { useEffect, useRef, useState } from 'react';
import useShop from '@/hooks/useShop';
import { InboxIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function UploadPage() {
  const { shop, loading: shopLoading } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState<Record<string, number>>({});
  const [messages, setMessages] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files);
    setFiles((prev) => [...prev, ...dropped]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files);
      setFiles((prev) => [...prev, ...selected]);
    }
  };

  const removeFile = (name: string) => {
    setFiles((prev) => prev.filter((f) => f.name !== name));
  };

  const handleUpload = async () => {
    if (!files.length || !shop) return;

    setUploading(true);
    const newProgress: Record<string, number> = {};
    const newMessages: string[] = [];

    for (const file of files) {
      const formData = new FormData();
      formData.append('image', file);

      try {
        // Upload to backend (handles Supabase + MakeIt3D)
        const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        if (!uploadRes.ok) throw new Error('Upload failed');
        const uploadData = await uploadRes.json();
        const imageUrl = uploadData.url;

        newProgress[file.name] = 100;
        setProgress((prev) => ({ ...prev, ...newProgress }));

        // Queue for processing
        const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ image_url: imageUrl, shop }),
        });

        const processData = await processRes.json();
        if (processRes.ok) {
          newMessages.push(`✅ ${file.name} uploaded and queued`);
        } else {
          throw new Error(processData.detail || 'Processing failed');
        }
      } catch (error) {
        console.error(error);
        newProgress[file.name] = 0;
        newMessages.push(`❌ ${file.name} failed`);
      }

      setProgress((prev) => ({ ...prev, ...newProgress }));
    }

    setMessages(newMessages);
    setFiles([]);
    setUploading(false);
  };

  if (shopLoading) {
    return <p className="text-center text-gray-500 mt-10">Loading shop...</p>;
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Upload Images</h1>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-gray-400 rounded-lg p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-black"
      >
        <InboxIcon className="h-12 w-12 text-gray-500" />
        <p className="text-gray-600">Drag & Drop files here or click to select</p>
        <input
          type="file"
          multiple
          ref={fileInputRef}
          className="hidden"
          onChange={handleFileChange}
        />
      </div>

      {files.length > 0 && (
        <div className="mt-6">
          <h2 className="font-semibold mb-2">Files to Upload:</h2>
          <ul className="space-y-2">
            {files.map((file) => (
              <li
                key={file.name}
                className="flex items-center justify-between border p-2 rounded"
              >
                <span className="truncate">{file.name}</span>
                <div className="flex items-center gap-3">
                  <div className="w-24 bg-gray-200 rounded">
                    <div
                      className="h-2 bg-blue-600 rounded"
                      style={{ width: `${progress[file.name] || 0}%` }}
                    />
                  </div>
                  <XMarkIcon
                    className="h-5 w-5 text-gray-500 hover:text-red-600 cursor-pointer"
                    onClick={() => removeFile(file.name)}
                  />
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!files.length || uploading}
        className="mt-6 px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : files.length > 1 ? 'Upload All' : 'Upload'}
      </button>

      {messages.length > 0 && (
        <div className="mt-6">
          {messages.map((msg, idx) => (
            <p key={idx} className="text-sm">
              {msg}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
