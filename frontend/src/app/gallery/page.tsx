import React, { useState, useCallback } from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  Button,
  BlockStack,
  Box,
  InlineStack,
  Grid,
  Thumbnail,
  Badge,
  Modal,
  Select,
  EmptyState
} from '@shopify/polaris';
import { ImageMajor } from '@shopify/polaris-icons';

interface ImageItem {
  id: string;
  originalUrl: string;
  processedUrl?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  productTitle: string;
  processType: string[];
  updatedAt: string;
}

export default function GalleryPage() {
  const [selectedImage, setSelectedImage] = useState<ImageItem | null>(null);
  const [filterStatus, setFilterStatus] = useState('all');

  // Sample data - replace with real data from API
  const images: ImageItem[] = [
    {
      id: '1',
      originalUrl: 'https://burst.shopifycdn.com/photos/business-woman-smiling-in-office.jpg',
      processedUrl: 'https://burst.shopifycdn.com/photos/business-woman-smiling-in-office-processed.jpg',
      status: 'completed',
      productTitle: 'Business Woman Portrait',
      processType: ['background_removal', 'optimization'],
      updatedAt: '2024-03-10T12:00:00Z'
    },
    // Add more sample images
  ];

  const statusOptions = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Processing', value: 'processing' },
    { label: 'Completed', value: 'completed' },
    { label: 'Failed', value: 'failed' }
  ];

  const filteredImages = filterStatus === 'all'
    ? images
    : images.filter(img => img.status === filterStatus);

  const getBadgeStatus = (status: string): 'success' | 'info' | 'critical' | 'attention' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'info';
      case 'failed':
        return 'critical';
      default:
        return 'attention';
    }
  };

  const handleImageClick = useCallback((image: ImageItem) => {
    setSelectedImage(image);
  }, []);

  return (
    <Page
      title="Image Gallery"
      primaryAction={
        <Button variant="primary" icon={ImageMajor}>Upload Images</Button>
      }
    >
      <BlockStack gap="5">
        {/* Filters */}
        <Card>
          <Box padding="3">
            <InlineStack align="space-between">
              <Select
                label="Filter by status"
                options={statusOptions}
                value={filterStatus}
                onChange={setFilterStatus}
              />
            </InlineStack>
          </Box>
        </Card>

        {/* Image Grid */}
        <Card>
          <Box padding="3">
            {filteredImages.length > 0 ? (
              <Grid>
                {filteredImages.map((image) => (
                  <Grid.Cell columnSpan={{ xs: 6, sm: 4, md: 3, lg: 2 }} key={image.id}>
                    <div onClick={() => handleImageClick(image)} style={{ cursor: 'pointer' }}>
                      <Card>
                        <Box padding="3">
                          <BlockStack gap="3">
                            <Thumbnail
                              source={image.processedUrl || image.originalUrl}
                              alt={image.productTitle}
                            />
                            <Text as="h3" variant="bodySm" fontWeight="bold">
                              {image.productTitle}
                            </Text>
                            <InlineStack gap="2">
                              <Badge tone={getBadgeStatus(image.status)}>
                                {image.status}
                              </Badge>
                              {image.processType.map((type) => (
                                <Badge key={type}>{type}</Badge>
                              ))}
                            </InlineStack>
                          </BlockStack>
                        </Box>
                      </Card>
                    </div>
                  </Grid.Cell>
                ))}
              </Grid>
            ) : (
              <EmptyState
                heading="No images found"
                image=""
                action={{
                  content: 'Upload Images',
                  icon: ImageMajor,
                  onAction: () => {/* Handle upload */}
                }}
              >
                <p>Upload some images to get started with AI processing.</p>
              </EmptyState>
            )}
          </Box>
        </Card>
      </BlockStack>

      {/* Image Preview Modal */}
      <Modal
        open={selectedImage !== null}
        onClose={() => setSelectedImage(null)}
        title={selectedImage?.productTitle || 'Image Preview'}
      >
        <Modal.Section>
          {selectedImage && (
            <BlockStack gap="5">
              <div style={{ display: 'flex', gap: '16px' }}>
                <div style={{ flex: 1 }}>
                  <Text as="h3" variant="headingSm">Original</Text>
                  <Box padding="3">
                    <img
                      src={selectedImage.originalUrl}
                      alt="Original"
                      style={{ width: '100%', height: 'auto' }}
                    />
                  </Box>
                </div>
                {selectedImage.processedUrl && (
                  <div style={{ flex: 1 }}>
                    <Text as="h3" variant="headingSm">Processed</Text>
                    <Box padding="3">
                      <img
                        src={selectedImage.processedUrl}
                        alt="Processed"
                        style={{ width: '100%', height: 'auto' }}
                      />
                    </Box>
                  </div>
                )}
              </div>
              <InlineStack gap="2">
                <Badge tone={getBadgeStatus(selectedImage.status)}>
                  {selectedImage.status}
                </Badge>
                {selectedImage.processType.map((type) => (
                  <Badge key={type}>{type}</Badge>
                ))}
              </InlineStack>
            </BlockStack>
          )}
        </Modal.Section>
      </Modal>
    </Page>
  );
} 