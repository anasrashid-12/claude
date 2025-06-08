import React, { useState, useEffect } from 'react';
import {
  Card,
  ResourceList,
  Badge,
  ProgressBar,
  Stack,
  Text,
  Banner,
} from '@shopify/polaris';

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

export default function ProcessingQueue() {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQueueItems();
    const interval = setInterval(fetchQueueItems, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchQueueItems = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/queue');
      const data = await response.json();
      setQueueItems(data);
      setError(null);
    } catch (err) {
      setError('Failed to load queue items');
    } finally {
      setIsLoading(false);
    }
  };

  const renderItem = (item: QueueItem) => {
    return (
      <ResourceList.Item id={item.id}>
        <Stack vertical>
          <Stack alignment="center" distribution="equalSpacing">
            <Text variant="bodyMd" fontWeight="bold">
              {item.fileName}
            </Text>
            <Badge status={getStatusBadge(item.status)}>
              {item.status}
            </Badge>
          </Stack>
          
          {item.status === 'processing' && (
            <Stack vertical spacing="tight">
              <ProgressBar
                progress={item.progress}
                size="small"
                tone={getProgressTone(item.progress)}
              />
              {item.estimatedTimeRemaining && (
                <Text variant="bodySm" color="subdued">
                  Estimated time remaining: {formatTime(item.estimatedTimeRemaining)}
                </Text>
              )}
            </Stack>
          )}

          {item.error && (
            <Banner status="critical">
              <Text variant="bodySm">{item.error}</Text>
            </Banner>
          )}
        </Stack>
      </ResourceList.Item>
    );
  };

  const getProgressTone = (progress: number): 'success' | 'highlight' => {
    return progress >= 90 ? 'success' : 'highlight';
  };

  const getStatusBadge = (status: QueueItem['status']): 'success' | 'attention' | 'warning' | 'critical' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'attention';
      case 'queued':
        return 'warning';
      case 'failed':
        return 'critical';
      default:
        return 'warning';
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ${Math.round(seconds % 60)}s`;
  };

  return (
    <Card title="Processing Queue">
      {error && (
        <Banner status="critical">
          <p>{error}</p>
        </Banner>
      )}

      <ResourceList
        items={queueItems}
        renderItem={renderItem}
        loading={isLoading}
        emptyState={
          <Stack vertical alignment="center" distribution="center">
            <Text variant="bodyMd" color="subdued">
              No items in queue
            </Text>
          </Stack>
        }
      />
    </Card>
  );
} 