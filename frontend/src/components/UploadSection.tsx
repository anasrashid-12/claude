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

type ItemStatus = 'idle' | 'uploading' | 'queued' | 'processing' | 'processed' | 'failed' | 'error';

type FileItem = {
  file: File;
  preview: string;
  progress: number;       // 0–100 upload progress
  status: ItemStatus;     // server/job status
  imageId?: string;       // returned from backend
  error?: string;
};

export default function UploadSection() {
  const { shop, loading: shopLoading, setShop } = useShop();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<FileItem[]>([]);
  const [selectedOption, setSelectedOption] = useState(OPTIONS[0].value);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    return () => {
      items.forEach(i => URL.revokeObjectURL(i.preview));
    };
  }, [items]);

  // Poll status for items that have an imageId and are not terminal
  useEffect(() => {
    const activeIds = items.filter(i =>
      i.imageId && (i.status === 'queued' || i.status === 'processing')
    );

    if (activeIds.length === 0) return;

    const interval = setInterval(async () => {
      try {
        const updates = await Promise.all(
          activeIds.map(async (it) => {
            const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/images/${it.imageId}`, {
              credentials: 'include',
            });
            if (!res.ok) return { id: it.imageId, status: it.status };
            const data = await res.json();
            return { id: it.imageId, status: (data?.status as ItemStatus) || it.status };
          })
        );

        setItems(prev =>
          prev.map(p => {
            const u = updates.find(x => x.id === p.imageId);
            if (!u) return p;
            return { ...p, status: u.status };
          })
        );
      } catch (e) {
        // ignore polling errors
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [items]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files || []).filter((file) => {
      if (!file.type.startsWith('image/')) return false;
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`❌ ${file.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`);
        return false;
      }
      return true;
    });

    const next: FileItem[] = selected.map(f => ({
      file: f,
      preview: URL.createObjectURL(f),
      progress: 0,
      status: 'idle',
    }));

    setItems(prev => [...prev, ...next]);
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

    const next: FileItem[] = dropped.map(f => ({
      file: f,
      preview: URL.createObjectURL(f),
      progress: 0,
      status: 'idle',
    }));
    setItems(prev => [...prev, ...next]);
  };

  const removeItem = (idx: number) => {
    setItems(prev => {
      const copy = [...prev];
      const toRemove = copy[idx];
      if (toRemove) URL.revokeObjectURL(toRemove.preview);
      copy.splice(idx, 1);
      return copy;
    });
  };

  const clearAll = () => {
    setItems(prev => {
      prev.forEach(p => URL.revokeObjectURL(p.preview));
      return [];
    });
  };

  // Single file upload with progress (XHR so we have onprogress)
  const uploadOne = (fileItem: FileItem, operation: string): Promise<{ imageId?: string; remaining_credits?: number }> => {
    return new Promise((resolve) => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', fileItem.file);
      formData.append('operation', operation);

      xhr.open('POST', `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, true);
      xhr.withCredentials = true;

      xhr.upload.onprogress = (evt) => {
        if (!evt.lengthComputable) return;
        const pct = Math.round((evt.loaded / evt.total) * 100);
        setItems(prev => prev.map(p => (p === fileItem ? { ...p, progress: pct, status: 'uploading' } : p)));
      };

      xhr.onreadystatechange = () => {
        if (xhr.readyState !== 4) return;

        try {
          const json = JSON.parse(xhr.responseText || '{}');

          if (xhr.status >= 200 && xhr.status < 300) {
            const remaining = json?.remaining_credits;
            const imageId = json?.id as string | undefined;

            if (remaining !== undefined) {
              setShop(prev => (prev ? { ...prev, credits: remaining } : prev));
            }

            setItems(prev => prev.map(p => (p === fileItem ? {
              ...p, status: 'queued', progress: 100, imageId
            } : p)));

            toast.success(`✅ ${fileItem.file.name} queued`);
            resolve({ imageId, remaining_credits: remaining });
          } else {
            const detail = json?.detail?.message || json?.detail || 'Upload failed';
            setItems(prev => prev.map(p => (p === fileItem ? { ...p, status: 'error', error: String(detail) } : p)));
            toast.error(`❌ ${fileItem.file.name}: ${detail}`);
            resolve({});
          }
        } catch (err) {
          setItems(prev => prev.map(p => (p === fileItem ? { ...p, status: 'error', error: 'Upload failed' } : p)));
          toast.error(`❌ ${fileItem.file.name}: Upload failed`);
          resolve({});
        }
      };

      xhr.send(formData);
    });
  };

  const handleUploadIndividually = async () => {
    if (!items.length || !shop) return;
    if ((shop.credits ?? 0) <= 0) {
      toast.error('❌ You have no credits left. Please purchase more.');
      return;
    }

    setUploading(true);
    for (const it of items) {
      if (it.status !== 'idle' && it.status !== 'error') continue;
      // stop if we ran out of credits mid-way
      if ((shop.credits ?? 0) <= 0) break;
      // eslint-disable-next-line no-await-in-loop
      await uploadOne(it, selectedOption);
    }
    setUploading(false);
  };

  // Optional: use /upload-multiple and then start polling each id the server returns
  const handleUploadBatch = async () => {
    if (!items.length || !shop) return;
    if ((shop.credits ?? 0) <= 0) {
      toast.error('❌ You have no credits left. Please purchase more.');
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      items.forEach(i => formData.append('files', i.file));
      formData.append('operation', selectedOption);

      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload-multiple`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        toast.error(`❌ ${data?.detail?.message || data?.detail || 'Batch upload failed'}`);
        setUploading(false);
        return;
      }

      const successes: Array<{ id: string; filename: string; remaining_credits?: number }> = data?.success || [];
      const failed: string[] = data?.failed || [];

      // update credits (use the last remaining_credits we got)
      const lastRemaining = successes.at(-1)?.remaining_credits;
      if (typeof lastRemaining === 'number') {
        setShop(prev => (prev ? { ...prev, credits: lastRemaining } : prev));
      }

      // attach ids to items and mark queued
      setItems(prev => prev.map(p => {
        const match = successes.find(s => s.filename === p.file.name);
        if (match) return { ...p, imageId: match.id, status: 'queued', progress: 100 };
        if (failed.includes(p.file.name)) return { ...p, status: 'error', error: 'Upload failed' };
        return p;
      }));

      toast.success(`🎉 Uploaded ${successes.length} of ${items.length} images`);
    } catch {
      toast.error('❌ Batch upload failed');
    }
    setUploading(false);
  };

  if (shopLoading) return <p className="text-gray-500 dark:text-gray-400">Loading shop...</p>;
  const noCredits = shop?.credits !== undefined && shop.credits <= 0;

  return (
    <div className="bg-white dark:bg-gray-900 p-4 sm:p-6 rounded-2xl shadow border border-gray-100 dark:border-gray-800 space-y-4 sm:space-y-6">
      {noCredits && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-md border border-red-400">
          You have 0 credits — purchase more to continue.
        </div>
      )}

      <div className="flex flex-col sm:flex-row justify-between items-center gap-3">
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">📤 Upload Images</h2>
        {items.length > 0 && (
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

      {items.length > 0 && (
        <div className="space-y-3">
          {items.map((it, idx) => (
            <div key={idx} className="flex gap-3 items-center p-2 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <div className="relative w-16 h-16 rounded-md overflow-hidden bg-gray-200 dark:bg-gray-700">
                <Image src={it.preview} alt={it.file.name} fill className="object-cover" />
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div className="truncate text-sm font-medium">{it.file.name}</div>
                  <div className="text-xs opacity-70 ml-2">
                    {it.status === 'idle' && 'Ready'}
                    {it.status === 'uploading' && `Uploading ${it.progress}%`}
                    {it.status === 'queued' && 'Queued'}
                    {it.status === 'processing' && 'Processing'}
                    {it.status === 'processed' && 'Done'}
                    {it.status === 'failed' && 'Failed'}
                    {it.status === 'error' && (it.error || 'Error')}
                  </div>
                </div>
                <div className="h-2 w-full bg-gray-200 dark:bg-gray-700 rounded mt-2 overflow-hidden">
                  <div
                    className={`h-2 ${it.status === 'processed' ? 'bg-green-500' : it.status === 'failed' || it.status === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}
                    style={{ width: `${it.status === 'idle' ? 0 : it.status === 'uploading' ? it.progress : 100}%` }}
                  />
                </div>
                {it.imageId && (
                  <div className="text-[11px] mt-1 opacity-70 truncate">ID: {it.imageId}</div>
                )}
              </div>

              <button
                onClick={() => removeItem(idx)}
                className="p-2 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30"
                aria-label="Remove"
              >
                <Trash2 size={16} className="text-red-600" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-2">
        <button
          onClick={handleUploadIndividually}
          disabled={!items.length || uploading || noCredits}
          className={`w-full sm:w-auto px-5 py-2.5 rounded-lg text-white ${noCredits ? 'bg-gray-400 cursor-not-allowed' : 'bg-black hover:bg-gray-800'} transition disabled:opacity-50`}
        >
          {uploading ? 'Uploading...' : `Upload Individually (${items.length})`}
        </button>

        <button
          onClick={handleUploadBatch}
          disabled={!items.length || uploading || noCredits}
          className={`w-full sm:w-auto px-5 py-2.5 rounded-lg text-white ${noCredits ? 'bg-gray-400 cursor-not-allowed' : 'bg-zinc-700 hover:bg-zinc-600'} transition disabled:opacity-50`}
        >
          {uploading ? 'Uploading...' : `Upload via /upload-multiple (${items.length})`}
        </button>
      </div>
    </div>
  );
}
