interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export class ApiRequestError extends Error {
  public code?: string;
  public details?: Record<string, any>;

  constructor(message: string, code?: string, details?: Record<string, any>) {
    super(message);
    this.name = 'ApiRequestError';
    this.code = code;
    this.details = details;
  }
}

export async function handleApiResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiError = {
      message: 'An unexpected error occurred',
    };

    try {
      errorData = await response.json();
    } catch {
      // If the error response is not JSON, use the status text
      errorData.message = response.statusText;
    }

    throw new ApiRequestError(
      errorData.message,
      errorData.code,
      errorData.details
    );
  }

  return response.json();
}

export async function fetchWithErrorHandling<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    return handleApiResponse<T>(response);
  } catch (error) {
    if (error instanceof ApiRequestError) {
      throw error;
    }

    throw new ApiRequestError(
      'Failed to connect to the server',
      'NETWORK_ERROR'
    );
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred';
} 