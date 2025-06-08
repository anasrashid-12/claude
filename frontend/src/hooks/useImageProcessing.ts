import { useState } from 'react';

interface ProcessedImage {
  id: string;
  originalUrl: string;
  processedUrl: string;
  status: string;
  createdAt: string;
}

interface ImageFile extends File {
  preview?: string;
}

interface ProcessingResult {
  url: string;
  status: string;
}

export function useImageProcessing() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ProcessingResult | null>(null);

  const processImage = async (file: File, type: string) => {
    try {
      setIsProcessing(true);
      setError(null);
      setResult(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to process image');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process image');
    } finally {
      setIsProcessing(false);
    }
  };

  const processMultiple = async (files: File[], type: string) => {
    const results = {
      successful: [] as ProcessingResult[],
      failed: [] as string[]
    };

    for (const file of files) {
      try {
        await processImage(file, type);
        if (result) {
          results.successful.push(result);
        }
      } catch (err) {
        results.failed.push(err instanceof Error ? err.message : 'Failed to process image');
      }
    }

    return results;
  };

  return {
    processImage,
    processMultiple,
    isProcessing,
    error,
    result,
  };
} 