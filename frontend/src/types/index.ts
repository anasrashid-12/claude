export interface ImageMetadata {
  width: number;
  height: number;
  format: string;
  size: number;
  processingType: string[];
}

export interface ProcessedImage {
  id: string;
  originalName: string;
  url: string;
  processedUrl: string | null;
  status: 'processing' | 'completed' | 'failed';
  error?: string;
  metadata: ImageMetadata;
  createdAt: string;
  updatedAt: string;
}

export interface ProcessingJob {
  id: string;
  imageId: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProcessingStats {
  totalProcessed: number;
  inQueue: number;
  failedJobs: number;
  averageProcessingTime: string;
  storageUsed: string;
  lastSync: string;
  successRate: number;
}

export interface ShopifyProduct {
  id: string;
  title: string;
  images: Array<{
    id: string;
    url: string;
    alt: string;
  }>;
  status: 'synced' | 'pending' | 'processing' | 'failed';
}

export interface ImageVersion {
  id: string;
  imageId: string;
  url: string;
  createdAt: string;
  processingType: string;
  metadata: ImageMetadata;
  status: 'active' | 'archived';
}

export interface ProcessingSettings {
  quality: number;
  format: 'jpeg' | 'png' | 'webp';
  maxWidth: number;
  maxHeight: number;
  preserveMetadata: boolean;
  compressionLevel: number;
  backgroundRemoval: {
    enabled: boolean;
    threshold: number;
    refinement: number;
  };
  watermark: {
    enabled: boolean;
    text: string;
    opacity: number;
    position: 'center' | 'bottomRight' | 'bottomLeft' | 'topRight' | 'topLeft';
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  hasNextPage: boolean;
  total: number;
}

export interface ImageFile extends File {
  preview?: string;
} 