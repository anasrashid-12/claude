import React, { useState } from 'react';
import {
  Card,
  ResourceList,
  ResourceItem,
  Thumbnail,
  Button,
  Box,
  InlineStack,
  Text,
  Badge,
} from '@shopify/polaris';
import { UI } from '../constants';
import { ImageGalleryProps, ImageStatus } from '../types';

export const ImageGallery: React.FC<ImageGalleryProps> = ({
  images,
  onSelectImage,
  onProcessImage,
}) => {
  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  const resourceListItems = images.map((image) => ({
    id: image.id,
    url: image.url,
    name: `${image.productTitle} - Image`,
    status: image.status,
  }));

  const getBadgeProps = (status: ImageStatus) => {
    switch (status) {
      case 'pending':
        return { status: 'info', children: 'Pending' };
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
      <ResourceList
        resourceName={{ singular: 'Image', plural: 'Images' }}
        items={resourceListItems}
        renderItem={(item) => {
          const { id, url, name, status } = item;

          return (
            <ResourceItem
              id={id}
              onClick={() => onSelectImage(id)}
              media={
                <Thumbnail
                  source={url}
                  alt={name}
                  size="large"
                />
              }
            >
              <Box padding={UI.SPACING.TIGHT}>
                <InlineStack align="space-between">
                  <Text as="h3" variant="bodyMd" fontWeight="bold">
                    {name}
                  </Text>
                  <InlineStack gap={UI.GAP.TIGHT}>
                    <Badge {...getBadgeProps(status)} />
                    <div onClick={(e) => e.stopPropagation()}>
                      <Button
                        disabled={status === 'processing'}
                        onClick={() => onProcessImage(id)}
                      >
                        Process Image
                      </Button>
                    </div>
                  </InlineStack>
                </InlineStack>
              </Box>
            </ResourceItem>
          );
        }}
        selectedItems={selectedItems}
        onSelectionChange={(items) => setSelectedItems(items as string[])}
        selectable
      />
    </Card>
  );
}; 