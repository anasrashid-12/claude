'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import Image from 'next/image';

interface UploadingFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  previewUrl?: string;
}

export default function UploadPage() {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substring(7),
      file,
      progress: 0,
      status: 'uploading' as const,
      previewUrl: URL.createObjectURL(file)
    }));

    setUploadingFiles((prev) => [...prev, ...newFiles]);

    // Process each file
    for (const fileData of newFiles) {
      try {
        // TODO: Implement actual file upload logic here
        // 1. Get staged upload URL
        // 2. Upload to S3
        // 3. Create file in Shopify
        // 4. Poll for processing status

        // Simulate upload progress
        await new Promise((resolve) => setTimeout(resolve, 2000));
        
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, status: 'completed', progress: 100 }
              : f
          )
        );
      } catch (error) {
        setUploadingFiles((prev) =>
          prev.map((f) =>
            f.id === fileData.id
              ? { ...f, status: 'error', error: 'Upload failed' }
              : f
          )
        );
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif']
    }
  });

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-12 text-center ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <div className="space-y-2">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 48 48"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 14v20c0 4.418 3.582 8 8 8h16c4.418 0 8-3.582 8-8V14m-16-4v16m-8-8h16"
                />
              </svg>
              <div className="text-sm text-gray-600">
                <label
                  htmlFor="file-upload"
                  className="relative cursor-pointer rounded-md font-medium text-blue-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 hover:text-blue-500"
                >
                  <span>Upload files</span>
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {uploadingFiles.length > 0 && (
        <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
          {uploadingFiles.map((file) => (
            <div key={file.id} className="p-4">
              <div className="flex items-center space-x-4">
                {file.previewUrl && (
                  <div className="flex-shrink-0 h-16 w-16 relative">
                    <Image
                      src={file.previewUrl}
                      alt={file.file.name}
                      fill
                      className="rounded-lg object-cover"
                    />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(file.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  {file.error && (
                    <p className="text-sm text-red-600">{file.error}</p>
                  )}
                </div>
                <div className="flex-shrink-0">
                  {file.status === 'uploading' && (
                    <div className="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-600 transition-all duration-300"
                        style={{ width: `${file.progress}%` }}
                      />
                    </div>
                  )}
                  {file.status === 'completed' && (
                    <svg
                      className="h-5 w-5 text-green-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  )}
                  {file.status === 'error' && (
                    <svg
                      className="h-5 w-5 text-red-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 