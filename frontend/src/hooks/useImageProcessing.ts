import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { processImage as processImageApi } from '../services/api';

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

export function useImageProcessing() {
  const [error, setError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async (file: ImageFile) => {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const result = await processImageApi(formData);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to process image';
        setError(errorMessage);
        throw err;
      }
    },
    onSuccess: () => {
      setError(null);
    }
  });

  const processImage = async (file: ImageFile, shouldRetry = true): Promise<ProcessedImage> => {
    try {
      const result = await mutation.mutateAsync(file);
      return result;
    } catch (err) {
      if (shouldRetry && err instanceof Error && err.message.includes('rate limit')) {
        // Wait and retry once if rate limited
        await new Promise(resolve => setTimeout(resolve, 1000));
        return processImage(file, false);
      }
      throw err;
    }
  };

  const processMultiple = async (files: ImageFile[]) => {
    const results = {
      successful: [] as ProcessedImage[],
      failed: [] as { file: ImageFile; error: string }[]
    };

    for (const file of files) {
      try {
        const result = await processImage(file);
        results.successful.push(result);
      } catch (err) {
        results.failed.push({
          file,
          error: err instanceof Error ? err.message : 'Unknown error'
        });
      }
    }

    return results;
  };

  return {
    processImage,
    processMultiple,
    isLoading: mutation.isPending,
    error,
    isError: mutation.isError,
    reset: mutation.reset,
    canRetry: !mutation.isPending
  };
} 