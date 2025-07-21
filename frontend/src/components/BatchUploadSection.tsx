'use client';

import { useState, useEffect, useRef } from 'react';
import useShop from '@/hooks/useShop';
import Image from 'next/image';
import { toast } from 'sonner';

const MAX_FILE_SIZE_MB = 5;

export default function BatchUploadSection() {
  const { shop, loading: shopLoading } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);

  useEffect(() => {
    if (!files.length) return;
    const urls = files.map((file) => URL.createObjectURL(file));
    setPreviews(urls);
    return () => urls.forEach((url) => URL.revokeObjectURL(url));
  }, [files]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []).filter((file) => {
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`❌ ${file.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`);
        return false;
      }
      return true;
    });
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

        const { url: imageUrl } = await uploadRes.json();

        const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image_url: imageUrl }),
        });

        if (!processRes.ok) throw new Error('Queue failed');

        newMessages.push(`✅ ${file.name} uploaded & queued`);
      } catch (err) {
        console.error(err);
        newMessages.push(`❌ ${file.name} failed`);
      }
    }

    setMessages(newMessages);
    setUploading(false);
    setFiles([]);
    setPreviews([]);
  };

  if (shopLoading) return <p className="text-gray-500 text-center mt-10">Loading...</p>;

  return (
    <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow space-y-4 border border-gray-200 dark:border-gray-800">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Batch Upload Images</h2>
        {files.length > 0 && (
          <button
            onClick={() => setFiles([])}
            className="text-red-500 text-sm hover:underline"
          >
            Clear All
          </button>
        )}
      </div>

      <input
        type="file"
        multiple
        accept="image/*"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="block w-full border border-gray-300 dark:border-gray-600 rounded p-2 dark:bg-gray-800"
      />

      {previews.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {previews.map((src, idx) => (
            <div key={idx} className="relative w-full h-40 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800">
              <Image src={src} alt={`Preview ${idx}`} fill className="object-cover" />
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!files.length || uploading}
        className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2.5 rounded transition disabled:opacity-50"
      >
        {uploading ? 'Uploading...' : `Upload ${files.length} Image${files.length > 1 ? 's' : ''}`}
      </button>

      {messages.length > 0 && (
        <div className="space-y-1 text-sm text-gray-700 dark:text-gray-300">
          {messages.map((msg, idx) => (
            <p key={idx}>{msg}</p>
          ))}
        </div>
      )}
    </div>
  );
}
