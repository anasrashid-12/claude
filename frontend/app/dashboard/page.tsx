'use client';

import React, { useState, useEffect } from 'react';
import { Page, Layout, Card, Button, Text, Box } from '@shopify/polaris';
import { ImageGallery } from '../../components/ImageGallery';
import { ProcessingQueue } from '../../components/ProcessingQueue';
import { LoadingState } from '../../components/LoadingState';
import { useWebSocket } from '../../hooks/useWebSocket';
import { useToast } from '../../hooks/useToast';
import { fetchWithErrorHandling, getErrorMessage } from '../../utils/api';
import { API_ENDPOINTS, WS_CONFIG, ERROR_MESSAGES, UI } from '../../constants';
import {
  Image,
  ProcessingTask,
  WebSocketMessage,
} from '../../types';

export default function DashboardPage() {
  const [images, setImages] = useState<Image[]>([]);
  const [tasks, setTasks] = useState<ProcessingTask[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { showToast, toastMarkup } = useToast();

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    const { type, data } = message;

    switch (type) {
      case 'task_update':
        setTasks((prevTasks) =>
          prevTasks.map((task) =>
            task.id === data.taskId
              ? { ...task, status: data.status as ProcessingTask['status'], progress: data.progress ?? task.progress }
              : task
          )
        );
        break;

      case 'task_complete':
        setTasks((prevTasks) =>
          prevTasks.map((task) =>
            task.id === data.taskId
              ? { ...task, status: 'completed', progress: 100 }
              : task
          )
        );
        // Update the corresponding image status
        setImages((prevImages) =>
          prevImages.map((img) =>
            img.id === data.imageId ? { ...img, status: 'completed' } : img
          )
        );
        showToast({
          content: 'Image processing completed successfully',
        });
        break;

      case 'task_error':
        setTasks((prevTasks) =>
          prevTasks.map((task) =>
            task.id === data.taskId
              ? { ...task, status: 'failed', error: data.error }
              : task
          )
        );
        // Update the corresponding image status
        setImages((prevImages) =>
          prevImages.map((img) =>
            img.id === data.imageId ? { ...img, status: 'failed' } : img
          )
        );
        showToast({
          content: `Error processing image: ${data.error}`,
          error: true,
        });
        break;
    }
  };

  const { isConnected } = useWebSocket({
    url: process.env.NEXT_PUBLIC_WS_URL || WS_CONFIG.DEFAULT_URL,
    onMessage: handleWebSocketMessage,
    onConnect: () => {
      console.log('Connected to WebSocket');
      showToast({ content: 'Connected to real-time updates' });
    },
    onDisconnect: () => {
      console.log('Disconnected from WebSocket');
      showToast({
        content: ERROR_MESSAGES.WEBSOCKET_DISCONNECTED,
        error: true,
      });
    },
  });

  useEffect(() => {
    fetchImagesAndTasks();
  }, []);

  const fetchImagesAndTasks = async () => {
    try {
      setIsLoading(true);
      const [imagesData, tasksData] = await Promise.all([
        fetchWithErrorHandling<Image[]>(API_ENDPOINTS.IMAGES),
        fetchWithErrorHandling<ProcessingTask[]>(API_ENDPOINTS.TASKS),
      ]);

      setImages(imagesData);
      setTasks(tasksData);
    } catch (error) {
      console.error('Error fetching data:', error);
      showToast({
        content: getErrorMessage(error),
        error: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleImageSelect = (imageId: string) => {
    // TODO: Implement image selection handling
    console.log('Selected image:', imageId);
  };

  const handleProcessImage = async (imageId: string) => {
    try {
      const newTask = await fetchWithErrorHandling<ProcessingTask>(API_ENDPOINTS.TASKS, {
        method: 'POST',
        body: JSON.stringify({ imageId }),
      });

      setTasks((prevTasks) => [...prevTasks, newTask]);
      
      // Update image status
      setImages((prevImages) =>
        prevImages.map((img) =>
          img.id === imageId ? { ...img, status: 'processing' } : img
        )
      );

      showToast({
        content: 'Started processing image',
      });
    } catch (error) {
      console.error('Error processing image:', error);
      showToast({
        content: ERROR_MESSAGES.PROCESSING_FAILED,
        error: true,
      });
    }
  };

  const handleRetryTask = async (taskId: string) => {
    try {
      const updatedTask = await fetchWithErrorHandling<ProcessingTask>(
        API_ENDPOINTS.TASK_RETRY(taskId),
        { method: 'POST' }
      );

      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, status: 'queued', error: undefined } : task
        )
      );

      showToast({
        content: 'Retrying image processing',
      });
    } catch (error) {
      console.error('Error retrying task:', error);
      showToast({
        content: ERROR_MESSAGES.RETRY_FAILED,
        error: true,
      });
    }
  };

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <Page title="AI Image Processing">
      <Layout>
        <Layout.Section>
          <Card>
            <Box padding={UI.SPACING.TIGHT}>
              <Text as="h2" variant="headingLg">
                Product Images
              </Text>
              {!isConnected && (
                <Text as="p" tone="critical">
                  Warning: Real-time updates are currently unavailable
                </Text>
              )}
            </Box>
            <ImageGallery
              images={images}
              onSelectImage={handleImageSelect}
              onProcessImage={handleProcessImage}
            />
          </Card>
        </Layout.Section>
        <Layout.Section>
          <ProcessingQueue
            tasks={tasks}
            onRetry={handleRetryTask}
          />
        </Layout.Section>
      </Layout>
      {toastMarkup}
    </Page>
  );    
} 