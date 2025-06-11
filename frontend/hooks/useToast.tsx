import { useState, useCallback } from 'react';
import { Toast } from '@shopify/polaris';

interface ToastOptions {
  content: string;
  error?: boolean;
  duration?: number;
}

export function useToast() {
  const [active, setActive] = useState(false);
  const [content, setContent] = useState('');
  const [error, setError] = useState(false);

  const showToast = useCallback(({ content, error = false, duration = 5000 }: ToastOptions) => {
    setContent(content);
    setError(error);
    setActive(true);

    setTimeout(() => {
      setActive(false);
    }, duration);
  }, []);

  const dismissToast = useCallback(() => {
    setActive(false);
  }, []);

  const toastMarkup = active ? (
    <Toast
      content={content}
      error={error}
      onDismiss={dismissToast}
    />
  ) : null;

  return {
    showToast,
    dismissToast,
    toastMarkup,
  };
} 