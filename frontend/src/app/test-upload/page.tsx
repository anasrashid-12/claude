'use client';

import { useState } from 'react';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { useShopify } from '../providers/ShopifyProvider';

export default function TestUpload() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const { shop } = useShopify();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('/api/process-images', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Test Image Upload</h1>
        {shop && (
          <p className="mb-4 text-gray-600">Connected to store: {shop}</p>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileChange}
              className="w-full"
            />
          </div>

          <button
            type="submit"
            disabled={uploading || files.length === 0}
            className={`px-4 py-2 rounded ${
              uploading || files.length === 0
                ? 'bg-gray-300 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
            }`}
          >
            {uploading ? 'Uploading...' : 'Upload Files'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        {results.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Upload Results:</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((result, index) => (
                <div key={index} className="border rounded p-4">
                  <p className="font-medium">{result.originalName}</p>
                  {result.error ? (
                    <p className="text-red-600">{result.error}</p>
                  ) : (
                    <>
                      <p className="text-sm text-gray-600">Status: {result.status}</p>
                      <img 
                        src={result.url} 
                        alt={result.alt} 
                        className="mt-2 max-w-full h-auto"
                      />
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
} 