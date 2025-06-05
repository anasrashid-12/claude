import { useCallback, useEffect, useState } from 'react';
import {
  BlockStack,
  Text,
  ProgressBar,
  Card,
  Banner,
  Spinner,
  EmptyState,
  ResourceList,
  Badge,
} from '@shopify/polaris';
import { get } from '../utils/api';
import { QueueStatus, QueueItem } from '../types/queue';

interface QueueResponse {
  success: boolean;
  error?: string;
interface QueueItem {
  id: string;
  fileName: string;
  progress: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  error?: string;
  createdAt: string;
  retryCount?: number;
  estimatedTimeRemaining?: number;
}

interface QueueResponse {
  success: boolean;
  error?: string;
  data?: QueueItem[];
}

export default function ProcessingQueue() {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchQueue = useCallback(async (isRefresh = false) => {
    try {
      setError(null);
      isRefresh ? setIsRefreshing(true) : setIsLoading(true);

      const data = await get<QueueResponse>('/queue');
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch queue data');
      }

      setQueueItems(data.data || []);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch queue';
      console.error('Failed to fetch queue:', error);
      setError(new Error(errorMessage));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(() => fetchQueue(true), 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, [fetchQueue]);

  const getProgressTone = (progress: number): 'success' | 'highlight' => {
    return progress === 100 ? 'success' : 'highlight';
  };

  const getStatusDetails = (item: QueueItem) => {
    if (item.status === 'processing') {
      return (
        <BlockStack gap="200">
          <ProgressBar
            progress={Math.round(item.progress)}
            size="small"
            tone={getProgressTone(item.progress)}
          />
          {item.estimatedTimeRemaining && (
            <Text as="p" variant="bodySm" tone="subdued">
              Estimated time remaining: {Math.ceil(item.estimatedTimeRemaining / 1000)}s
            </Text>
          )}
        </BlockStack>
      );
    }

    if (item.status === 'failed') {
      return (
        <Text as="p" variant="bodySm" tone="critical">
          {item.error || 'Processing failed'}
          {item.retryCount && ` (Retry ${item.retryCount})`}
        </Text>
      );
    }

    return null;
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '32px' }}>
        <Spinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Banner tone="critical" onDismiss={() => setError(null)}>
        <p>Failed to load processing queue: {error.message}</p>
      </Banner>
    );
  }

  if (queueItems.length === 0) {
    return (
      <Card>
        <EmptyState
          heading="No active jobs"
          image="/empty-state-images/no-jobs.svg"
        >
          <p>There are no images being processed at the moment.</p>
        </EmptyState>
      </Card>
    );
  }

  return (
    <Card>
      <BlockStack gap="400">
        <Text as="h2" variant="headingMd">Processing Queue</Text>
        {queueItems.map((item) => (
          <Card key={item.id}>
            <BlockStack gap="200">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text as="span" variant="bodyMd" fontWeight="bold">{item.fileName}</Text>
                <Text
                  as="span"
                  variant="bodySm"
                  tone={
                    item.status === 'failed'
                      ? 'critical'
                      : item.status === 'completed'
                      ? 'success'
                      : 'subdued'
                  }
                >
                  {item.status}
                </Text>
              </div>
              
              {getStatusDetails(item)}

              <Text as="p" variant="bodySm" tone="subdued">
                Started: {new Date(item.createdAt).toLocaleString()}
              </Text>
            </BlockStack>
          </Card>
        ))}
      </BlockStack>
    </Card>
  );
} 