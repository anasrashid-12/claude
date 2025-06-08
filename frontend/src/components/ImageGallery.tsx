import React, { useState, useEffect } from 'react';
import { 
  Card, 
  ResourceList, 
  Thumbnail, 
  Button, 
  Stack, 
  Badge, 
  Modal,
  TextContainer,
  Select,
  Banner
} from '@shopify/polaris';
import { ProcessingType } from '../types/database';
import { useImageProcessing } from '../hooks/useImageProcessing';

interface ProcessedImage {
  id: string;
  originalUrl: string;
  processedUrl: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  productTitle: string;
  processTypes: ProcessingType[];
  updatedAt: string;
}

export default function ImageGallery() {
  const [images, setImages] = useState<ProcessedImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<ProcessedImage | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [modalActive, setModalActive] = useState(false);
  const [processingType, setProcessingType] = useState<ProcessingType[]>([]);
  const [error, setError] = useState<string | null>(null);
  
  const { processImage } = useImageProcessing();

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      const response = await fetch('/api/images');
      const data = await response.json();
      setImages(data);
    } catch (err) {
      setError('Failed to load images');
    }
  };

  const handleProcessImage = async (image: ProcessedImage) => {
    setIsProcessing(true);
    setError(null);
    
    try {
      await processImage(image.id, processingType);
      await fetchImages(); // Refresh the list
    } catch (err) {
      setError('Failed to process image');
    } finally {
      setIsProcessing(false);
      setModalActive(false);
    }
  };

  const renderItem = (item: ProcessedImage) => {
    const media = (
      <Thumbnail
        source={item.processedUrl || item.originalUrl}
        alt={item.productTitle}
        size="large"
      />
    );

    const shortcutActions = [
      {
        content: 'Process',
        onAction: () => {
          setSelectedImage(item);
          setModalActive(true);
        },
      },
    ];

    return (
      <ResourceList.Item
        id={item.id}
        media={media}
        shortcutActions={shortcutActions}
        persistActions
      >
        <Stack>
          <Stack.Item fill>
            <h3>{item.productTitle}</h3>
          </Stack.Item>
          <Stack.Item>
            <Badge status={getStatusColor(item.status)}>
              {item.status}
            </Badge>
          </Stack.Item>
        </Stack>
      </ResourceList.Item>
    );
  };

  const getStatusColor = (
    status: string
  ): 'success' | 'attention' | 'warning' | 'critical' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'attention';
      case 'pending':
        return 'warning';
      case 'failed':
        return 'critical';
      default:
        return 'warning';
    }
  };

  return (
    <>
      <Card>
        {error && (
          <Banner status="critical">
            <p>{error}</p>
          </Banner>
        )}
        
        <ResourceList
          items={images}
          renderItem={renderItem}
          showHeader
          resourceName={{ singular: 'image', plural: 'images' }}
        />
      </Card>

      <Modal
        open={modalActive}
        onClose={() => setModalActive(false)}
        title="Process Image"
        primaryAction={{
          content: 'Process',
          onAction: () => selectedImage && handleProcessImage(selectedImage),
          loading: isProcessing,
        }}
        secondaryActions={[
          {
            content: 'Cancel',
            onAction: () => setModalActive(false),
          },
        ]}
      >
        <Modal.Section>
          <TextContainer>
            <Select
              label="Processing Type"
              options={[
                { label: 'Background Removal', value: 'background_removal' },
                { label: 'Resize', value: 'resize' },
                { label: 'Optimize', value: 'optimize' },
              ]}
              onChange={(value) => setProcessingType([value as ProcessingType])}
              value={processingType[0]}
            />
          </TextContainer>
        </Modal.Section>
      </Modal>
    </>
  );
} 