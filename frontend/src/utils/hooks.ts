import { useState, useEffect, useCallback } from 'react';
import { ProcessingStats, ProcessingJob, ProcessingSettings } from '../types';
import { api } from './api';

export function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number = 5000,
  enabled: boolean = true
) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetch = useCallback(async () => {
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An error occurred'));
    } finally {
      setIsLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    if (!enabled) return;

    fetch();
    const timer = setInterval(fetch, interval);

    return () => clearInterval(timer);
  }, [fetch, interval, enabled]);

  return { data, error, isLoading, refetch: fetch };
}

export function useProcessingStats() {
  return usePolling<ProcessingStats>(async () => {
    const response = await api.getProcessingStats();
    return response.data as ProcessingStats;
  });
}

export function useQueueStatus() {
  return usePolling<ProcessingJob[]>(async () => {
    const response = await api.getQueueStatus();
    return response.data as ProcessingJob[];
  });
}

export function useProcessingSettings() {
  const [settings, setSettings] = useState<ProcessingSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchSettings = useCallback(async () => {
    try {
      const response = await api.getSettings();
      setSettings(response.data as ProcessingSettings);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load settings'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const updateSettings = useCallback(async (newSettings: ProcessingSettings) => {
    try {
      await api.updateSettings(newSettings as unknown as Record<string, unknown>);
      setSettings(newSettings);
      return true;
    } catch (error) {
      return false;
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return {
    settings,
    isLoading,
    error,
    updateSettings,
    refetch: fetchSettings
  };
}

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
} 