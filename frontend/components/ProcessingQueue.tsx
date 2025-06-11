import React from 'react';
import {
  Card,
  ResourceList,
  ResourceItem,
  Text,
  Badge,
  ProgressBar,
  Box,
  InlineStack,
  Button,
} from '@shopify/polaris';
import { UI } from '../constants';
import { ProcessingQueueProps, TaskStatus } from '../types';

export const ProcessingQueue: React.FC<ProcessingQueueProps> = ({
  tasks,
  onRetry,
}) => {
  const getBadgeProps = (status: TaskStatus) => {
    switch (status) {
      case 'queued':
        return { status: 'info', children: 'Queued' };
      case 'processing':
        return { status: 'attention', children: 'Processing' };
      case 'completed':
        return { status: 'success', children: 'Completed' };
      case 'failed':
        return { status: 'critical', children: 'Failed' };
    }
  };

  return (
    <Card>
      <Box padding={UI.SPACING.TIGHT}>
        <Text as="h2" variant="headingMd">
          Processing Queue
        </Text>
      </Box>
      <ResourceList
        resourceName={{ singular: 'Task', plural: 'Tasks' }}
        items={tasks}
        renderItem={(task) => (
          <ResourceItem
            id={task.id}
            onClick={() => {}}
          >
            <Box padding={UI.SPACING.TIGHT}>
              <InlineStack align="space-between">
                <Box>
                  <Text as="h3" variant="bodyMd" fontWeight="bold">
                    {task.productTitle}
                  </Text>
                  {task.error && (
                    <Text as="p" variant="bodySm" tone="critical">
                      Error: {task.error}
                    </Text>
                  )}
                </Box>
                <InlineStack gap={UI.GAP.TIGHT}>
                  <Badge {...getBadgeProps(task.status)} />
                  {task.status === 'processing' && (
                    <Box minWidth="200px">
                      <ProgressBar
                        progress={task.progress}
                        size="small"
                        tone={task.progress === 100 ? 'success' : 'highlight'}
                      />
                    </Box>
                  )}
                  {task.status === 'failed' && (
                    <div onClick={(e) => e.stopPropagation()}>
                      <Button onClick={() => onRetry(task.id)}>Retry</Button>
                    </div>
                  )}
                </InlineStack>
              </InlineStack>
            </Box>
          </ResourceItem>
        )}
      />
    </Card>
  );
}; 