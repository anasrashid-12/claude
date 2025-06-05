const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

async function handleResponse<T>(response: Response): Promise<T> {
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error || 'An error occurred');
  }
  
  return data;
}

export async function processImage(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/images/process`, {
    method: 'POST',
    body: formData,
  });
  
  return handleResponse(response);
}

export async function listImages(page = 1, limit = 20) {
  const response = await fetch(
    `${API_BASE_URL}/images?page=${page}&limit=${limit}`
  );
  
  return handleResponse(response);
}

export async function getQueueStatus() {
  const response = await fetch(`${API_BASE_URL}/queue/status`);
  return handleResponse(response);
}

export async function getProcessingStats() {
  const response = await fetch(`${API_BASE_URL}/stats/processing`);
  return handleResponse(response);
}

export async function getResourceStats() {
  const response = await fetch(`${API_BASE_URL}/stats/resources`);
  return handleResponse(response);
} 