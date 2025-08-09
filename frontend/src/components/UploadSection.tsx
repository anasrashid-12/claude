'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import useShop from '@/hooks/useShop';
import { Trash2 } from 'lucide-react';
import { toast } from 'sonner';

const OPTIONS = [
  { label: 'Remove Background', value: 'remove-background' },
  { label: 'Upscale', value: 'upscale' },
  { label: 'Downscale', value: 'downscale' },
];

const MAX_FILE_SIZE_MB = 5;

export default function UploadSection() {
  // Destructure setShop from useShop as well
  const { shop, loading: shopLoading, setShop } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedOption, setSelectedOption] = useState(OPTIONS[0].value);

  useEffect(() => {
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
    setFiles((prev) => [...prev, ...selected]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const dropped = Array.from(e.dataTransfer.files).filter((file) => {
      if (!file.type.startsWith('image/')) return false;
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`❌ ${file.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`);
        return false;
      }
      return true;
    });
    setFiles((prev) => [...prev, ...dropped]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== index));
  };

  const clearAll = () => {
    setFiles([]);
  };

  const handleUpload = async () => {
    if (!files.length || !shop) return;

    if (shop.credits <= 0) {
      toast.error("❌ You have no credits left. Please purchase more.");
      return;
    }

    setUploading(true);
    let successCount = 0;

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('operation', selectedOption);

        const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        const data = await uploadRes.json();

        if (!uploadRes.ok) {
          if (uploadRes.status === 402 && data?.message) {
            toast.error(`❌ ${data.message}`);
          } else {
            toast.error(`❌ ${file.name} failed`);
          }
          continue;
        }

        // Update credits immediately after successful upload
        setShop((prev) =>
          prev ? { ...prev, credits: data.remaining_credits } : prev
        );

        toast.success(`✅ ${file.name} uploaded & processing started (ID: ${data.id})`);
        successCount++;
      } catch (err) {
        console.error(err);
        toast.error(`❌ ${file.name} failed`);
      }
    }

    setUploading(false);
    clearAll();

    if (successCount > 0) {
      toast.success(`🎉 Uploaded ${successCount} image${successCount > 1 ? 's' : ''}`);
    }
  };

  if (shopLoading) return <p className="text-gray-500 dark:text-gray-400">Loading shop...</p>;

  const noCredits = shop?.credits !== undefined && shop.credits <= 0;

  return (
    <div className="bg-white dark:bg-gray-900 p-4 sm:p-6 rounded-2xl shadow border border-gray-100 dark:border-gray-800 space-y-4 sm:space-y-6">
      {/* Banner for zero credits */}
      {noCredits && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md border border-red-400">
          You have 0 credits — purchase more to continue.
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-center gap-3">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">📤 Upload Images</h2>
        {files.length > 0 && (
          <button onClick={clearAll} className="text-sm text-red-500 hover:underline">
            Clear All
          </button>
        )}
      </div>

      <select
        value={selectedOption}
        onChange={(e) => setSelectedOption(e.target.value)}
        className="w-full border rounded-md p-2 text-sm dark:bg-gray-800 dark:border-gray-600"
      >
        {OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className="w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 sm:p-6 text-center cursor-pointer hover:border-blue-400 dark:hover:border-blue-600 transition"
      >
        <input
          type="file"
          accept="image/*"
          multiple
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Click or drag & drop image(s) here (Max {MAX_FILE_SIZE_MB}MB each)
        </p>
      </div>

      {previews.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {previews.map((src, idx) => (
            <div
              key={idx}
              className="relative w-full aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800 shadow-sm group"
            >
              <Image src={src} alt={`Preview ${idx}`} fill className="object-cover" />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile(idx);
                }}
                className="absolute top-1 right-1 bg-white dark:bg-gray-900 bg-opacity-80 rounded-full p-1 shadow hover:bg-red-100"
              >
                <Trash2 size={16} className="text-red-600" />
              </button>
              <div className="absolute bottom-0 left-0 w-full bg-black/50 text-white text-xs px-2 py-1 truncate">
                {files[idx]?.name}
              </div>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!files.length || uploading || noCredits}
        className={`w-full sm:w-auto px-5 py-2.5 rounded-lg text-white ${
          noCredits ? 'bg-gray-400 cursor-not-allowed' : 'bg-black hover:bg-gray-800'
        } transition disabled:opacity-50`}
      >
        {uploading
          ? 'Uploading...'
          : noCredits
          ? 'No credits left'
          : `Upload ${files.length} Image${files.length > 1 ? 's' : ''}`}
      </button>
    </div>
  );
}
