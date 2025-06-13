import { UI } from '../constants';

// Polaris types
// Polaris-compatible spacing
export type Spacing =
  | 'none'
  | 'extraTight'
  | 'tight'
  | 'base'
  | 'loose'
  | 'extraLoose'
  | 'extraExtraLoose';
export type Breakpoint = 'mobile' | 'tablet' | 'desktop' | 'wide';

// Domain types
export type ImageStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type TaskStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface Image {
  id: string;
  url: string;
  productId: string;
  productTitle: string;
  status: ImageStatus;
}

export interface ProcessingTask {
  id: string;
  imageId: string;
  productTitle: string;
  status: TaskStatus;
  progress: number;
  error?: string;
}

// WebSocket types
export type WebSocketMessageType = 'task_update' | 'task_complete' | 'task_error';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: {
    taskId: string;
    imageId?: string;
    status: string;
    progress?: number;
    error?: string;
  };
}

// API types
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

// Component props
export interface ImageGalleryProps {
  images: Image[];
  onSelectImage: (imageId: string) => void;
  onProcessImage: (imageId: string) => void;
}

export interface ProcessingQueueProps {
  tasks: ProcessingTask[];
  onRetry: (taskId: string) => void;
}

export interface UseWebSocketOptions {
  url: string;
  onMessage: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export interface ToastOptions {
  content: string;
  error?: boolean;
  duration?: number;
} 