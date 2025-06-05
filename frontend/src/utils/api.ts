import { toast } from 'react-hot-toast';
import { ApiResponse, PaginatedResponse } from '../types';

interface ApiErrorResponse {
  message: string;
  error?: string;
}

interface ApiRequestOptions<T = unknown> extends Omit<RequestInit, 'body'> {
  body?: T;
}

class ApiError extends Error {
  status: number;
  error?: string;
  
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');
  
  if (!response.ok) {
    if (isJson) {
      const error = await response.json() as ApiErrorResponse;
      throw new ApiError(error.message || 'An error occurred', response.status);
    }
    throw new ApiError('An error occurred', response.status);
  }

  if (isJson) {
    const data = await response.json();
    return data as T;
  }

  throw new ApiError('Invalid response format', response.status);
}

async function apiRequest<T, B = unknown>(
  endpoint: string, 
  options?: ApiRequestOptions<B>
): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    ...options,
    body: options?.body ? JSON.stringify(options.body) : undefined,
  } as RequestInit);

  return handleResponse<T>(response);
}

export async function get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`/api${endpoint}`, window.location.origin);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  const response = await fetch(url.toString(), {
    headers: {
      'Accept': 'application/json',
    },
  });

  return handleResponse<T>(response);
}

export async function post<T>(endpoint: string, data?: unknown): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: data ? JSON.stringify(data) : undefined,
  });

  return handleResponse<T>(response);
}

export async function put<T>(endpoint: string, data: unknown): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(data),
  });

  return handleResponse<T>(response);
}

export async function del<T>(endpoint: string): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    method: 'DELETE',
    headers: {
      'Accept': 'application/json',
    },
  });

  return handleResponse<T>(response);
}

interface UploadOptions {
  onUploadProgress?: (progressEvent: { loaded: number; total: number }) => void;
  data?: Record<string, string>;
}

export async function upload<T>(
  endpoint: string,
  files: File[],
  options?: UploadOptions
): Promise<T> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  if (options?.data) {
    Object.entries(options.data).forEach(([key, value]) => {
      formData.append(key, value);
    });
  }

  const xhr = new XMLHttpRequest();
  
  return new Promise<T>((resolve, reject) => {
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && options?.onUploadProgress) {
        options.onUploadProgress({
          loaded: event.loaded,
          total: event.total
        });
      }
    });

    xhr.addEventListener('load', async () => {
      try {
        const response = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(response);
        } else {
          reject(new ApiError(response.message || 'Upload failed', xhr.status));
        }
      } catch (error) {
        reject(new ApiError('Invalid response format', xhr.status));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new ApiError('Network error occurred', 0));
    });

    xhr.open('POST', `/api${endpoint}`);
    xhr.send(formData);
  });
}

export async function uploadImages(files: File[], onProgress?: (progress: number) => void) {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));

  try {
    const response = await fetch('/api/images/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json() as ApiError;
      throw new Error(error.error || 'Failed to upload images');
    }

    return response.json();
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'Failed to upload images');
    throw error;
  }
}

interface SyncProductsRequest {
  productIds: string[];
}

interface RevertImageRequest {
  imageId: string;
  versionId: string;
}

export const api = {
  // Products
  getProducts: (page: number, query?: string) => 
    apiRequest<PaginatedResponse<any>>(`/products?page=${page}${query ? `&query=${query}` : ''}`),
  
  syncProducts: (productIds: string[]) =>
    apiRequest<ApiResponse<void>, SyncProductsRequest>('/products/sync', { 
      method: 'POST', 
      body: { productIds }
    }),
  
  getSyncStatus: () =>
    apiRequest<ApiResponse<{ status: string }>>('/products/sync/status'),

  // Images
  getImageHistory: () =>
    apiRequest<ApiResponse<any>>('/images/history'),
  
  revertImage: (imageId: string, versionId: string) =>
    apiRequest<ApiResponse<void>, RevertImageRequest>('/images/revert', { 
      method: 'POST', 
      body: { imageId, versionId }
    }),

  // Processing
  getProcessingStats: () =>
    apiRequest<ApiResponse<any>>('/stats'),
  
  getQueueStatus: () =>
    apiRequest<ApiResponse<any>>('/queue'),

  // Settings
  getSettings: () =>
    apiRequest<ApiResponse<any>>('/settings/processing'),
  
  updateSettings: (settings: Record<string, unknown>) =>
    apiRequest<ApiResponse<void>, Record<string, unknown>>('/settings/processing', { 
      method: 'POST', 
      body: settings 
    })
}; 