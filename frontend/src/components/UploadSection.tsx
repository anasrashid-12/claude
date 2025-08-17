'use client';

import { useEffect, useRef, useState } from 'react';
import Image from 'next/image';
import useShop from '@/hooks/useShop';
import { useCredits } from '@/components/CreditsProvider';
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
  progress: number;
  status: ItemStatus;
  imageId?: string;
  error?: string;
};

export default function UploadSection() {
  const { shop, loading: shopLoading, setShop } = useShop();
  const { refreshCredits } = useCredits();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [items, setItems] = useState<FileItem[]>([]);
  const [selectedOption, setSelectedOption] = useState(OPTIONS[0].value);
  const [uploading, setUploading] = useState(false);

  useEffect(() => () => items.forEach(i => URL.revokeObjectURL(i.preview)), [items]);

  const handleFiles = (files: FileList) => {
    const selected = Array.from(files).filter(f => {
      if (!f.type.startsWith('image/')) return false;
      if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        toast.error(`❌ ${f.name} exceeds ${MAX_FILE_SIZE_MB}MB limit`);
        return false;
      }
      return true;
    });

    const nextItems: FileItem[] = selected.map(f => ({
      file: f,
      preview: URL.createObjectURL(f),
      progress: 0,
      status: 'idle',
    }));

    setItems(prev => [...prev, ...nextItems]);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    handleFiles(e.dataTransfer.files);
  };

  const removeItem = (idx: number) => {
    setItems(prev => {
      const copy = [...prev];
      URL.revokeObjectURL(copy[idx].preview);
      copy.splice(idx, 1);
      return copy;
    });
  };

  const clearAll = () => {
    setItems(prev => {
      prev.forEach(i => URL.revokeObjectURL(i.preview));
      return [];
    });
  };

  const uploadOne = (fileItem: FileItem): Promise<void> =>
    new Promise(resolve => {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', fileItem.file);
      formData.append('operation', selectedOption);
  
      xhr.open('POST', `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, true);
      xhr.withCredentials = true;
  
      xhr.upload.onprogress = evt => {
        if (!evt.lengthComputable) return;
        const pct = Math.round((evt.loaded / evt.total) * 100);
        setItems(prev =>
          prev.map(p =>
            p === fileItem ? { ...p, progress: pct, status: 'uploading' } : p
          )
        );
      };
  
      xhr.onreadystatechange = async () => {
        if (xhr.readyState !== 4) return;
        try {
          const json = JSON.parse(xhr.responseText || '{}');
          if (xhr.status >= 200 && xhr.status < 300) {
            const imageId = json?.id;
  
            // ✅ Topbar ke credits refresh karo
            await refreshCredits();
  
            // ✅ Remove uploaded item from list
            setItems(prev => prev.filter(p => p.preview !== fileItem.preview));
  
            toast.success(`✅ ${fileItem.file.name} uploaded & cleared`);
          } else {
            const detail =
              json?.detail?.message || json?.detail || 'Upload failed';
            setItems(prev =>
              prev.map(p =>
                p === fileItem ? { ...p, status: 'error', error: detail } : p
              )
            );
            toast.error(`❌ ${fileItem.file.name}: ${detail}`);
          }
        } catch {
          setItems(prev =>
            prev.map(p =>
              p === fileItem
                ? { ...p, status: 'error', error: 'Upload failed' }
                : p
            )
          );
          toast.error(`❌ ${fileItem.file.name}: Upload failed`);
        } finally {
          resolve();
        }
      };
  
      xhr.send(formData);
    });
  
  const handleUploadIndividually = async () => {
    if (!items.length || !shop) return;
    if ((shop.credits ?? 0) <= 0) {
      toast.error('❌ You have no credits left. Please purchase more.');
      return;
    }
  
    setUploading(true);
    for (const it of items) {
      if (it.status !== 'idle' && it.status !== 'error') continue;
      if ((shop.credits ?? 0) <= 0) break; // stop if no credits left
      await uploadOne(it);
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
          <button onClick={clearAll} className="text-sm text-red-500 hover:underline">Clear All</button>
        )}
      </div>

      <select
        value={selectedOption}
        onChange={(e) => setSelectedOption(e.target.value)}
        className="w-full border rounded-md p-2 text-sm dark:bg-gray-800 dark:border-gray-600"
      >
        {OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
      </select>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => fileInputRef.current?.click()}
        className="w-full border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 sm:p-6 text-center cursor-pointer hover:border-blue-400 dark:hover:border-blue-600 transition"
      >
        <input type="file" accept="image/*" multiple ref={fileInputRef} onChange={e => handleFiles(e.target.files!)} className="hidden" />
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
                  <div className={`h-2 ${it.status === 'processed' ? 'bg-green-500' : it.status === 'failed' || it.status === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}
                       style={{ width: `${it.status === 'idle' ? 0 : it.status === 'uploading' ? it.progress : 100}%` }} />
                </div>
                {it.imageId && <div className="text-[11px] mt-1 opacity-70 truncate">ID: {it.imageId}</div>}
              </div>

              <button onClick={() => removeItem(idx)} className="p-2 rounded-md hover:bg-red-100 dark:hover:bg-red-900/30" aria-label="Remove">
                <Trash2 size={16} className="text-red-600" />
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={handleUploadIndividually}
        disabled={!items.length || uploading || noCredits}
        className={`w-full sm:w-auto px-5 py-2.5 rounded-lg text-white ${noCredits ? 'bg-gray-400 cursor-not-allowed' : 'bg-black hover:bg-gray-800'} transition disabled:opacity-50`}
      >
        {uploading ? 'Uploading...' : `Upload (${items.length})`}
      </button>
    </div>
  );
}
