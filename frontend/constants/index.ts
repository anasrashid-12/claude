// API endpoints
export const API_ENDPOINTS = {
  IMAGES: '/api/images',
  TASKS: '/api/tasks',
  TASK_RETRY: (taskId: string) => `/api/tasks/${taskId}/retry`,
};

// WebSocket configuration
export const WS_CONFIG = {
  DEFAULT_URL: 'ws://localhost:8000/ws',
  RECONNECT_DELAY: 5000,
};

// Toast notifications
export const TOAST_CONFIG = {
  DEFAULT_DURATION: 5000,
  ERROR_DURATION: 7000,
};

// Image processing
export const IMAGE_PROCESSING = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
};

import type { Spacing } from '../types'; // path to your types

export const UI = {
  SPACING: {
    NONE: 'none' as Spacing,
    EXTRA_TIGHT: 'extraTight' as Spacing,
    TIGHT: 'tight' as Spacing,
    BASE: 'base' as Spacing,
    LOOSE: 'loose' as Spacing,
    EXTRA_LOOSE: 'extraLoose' as Spacing,
    EXTRA_EXTRA_LOOSE: 'extraExtraLoose' as Spacing,
  },

  GAP: {
    NONE: 'none' as Spacing,
    EXTRA_TIGHT: 'extraTight' as Spacing,
    TIGHT: 'tight' as Spacing,
    BASE: 'base' as Spacing,
    LOOSE: 'loose' as Spacing,
    EXTRA_LOOSE: 'extraLoose' as Spacing,
    EXTRA_EXTRA_LOOSE: 'extraExtraLoose' as Spacing,
  },

  BREAKPOINTS: {
    MOBILE: 'mobile',
    TABLET: 'tablet',
    DESKTOP: 'desktop',
    WIDE: 'wide',
  } as const,
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Failed to connect to the server',
  UNEXPECTED_ERROR: 'An unexpected error occurred',
  PROCESSING_FAILED: 'Failed to process image',
  RETRY_FAILED: 'Failed to retry task',
  WEBSOCKET_DISCONNECTED: 'Disconnected from real-time updates',
};
