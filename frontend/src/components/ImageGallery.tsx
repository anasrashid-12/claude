import { useState, useCallback, useEffect } from 'react';
import {
  DropZone,
  BlockStack,
  InlineStack,
  Thumbnail,
  Text,
  Button,
  Banner,
  Card,
  Grid,
  Spinner,
  Modal,
  Badge,
  EmptyState,
  Icon,
  ProgressBar,
  Tooltip,
} from '@shopify/polaris';
import {
  ImageMajor,
  DeleteMajor,
  ViewMajor,
  RefreshMajor
} from '@shopify/polaris-icons';
import { get, del } from '../utils/api';
import { ProcessedImage, ImageFile, ApiResponse, PaginatedResponse } from '../types';
import { useImageProcessing } from '../hooks/useImageProcessing';
import toast from 'react-hot-toast';

const PAGE_SIZE = 20;
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export default function ImageGallery() {
  const [files, setFiles] = useState<ImageFile[]>([]);
  const [processedImages, setProcessedImages] = useState<ProcessedImage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [selectedImage, setSelectedImage] = useState<ProcessedImage | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const { processImage, isUploading, progress } = useImageProcessing({
    onSuccess: (image) => {
      setProcessedImages((prev) => [image, ...prev]);
      setFiles([]); // Clear uploaded files after successful processing
      toast.success('Image processed successfully');
    },
    onError: (error) => {
      toast.error(`Processing failed: ${error.message}`);
    },
  });

  const fetchProcessedImages = async (isRefresh = false) => {
    try {
      setError(null);
      isRefresh ? setIsRefreshing(true) : setIsLoading(true);
      
      const response = await get<ApiResponse<PaginatedResponse<ProcessedImage>>>('/images', {
        page: page.toString(),
        limit: PAGE_SIZE.toString(),
      });

      if (!response.success) {
        throw new Error(response.error || 'Failed to load images');
      }

      if (response.data) {
        if (page === 1 || isRefresh) {
          setProcessedImages(response.data.items);
        } else {
          setProcessedImages((prev) => [...prev, ...response.data.items]);
        }
        setHasNextPage(response.data.hasNextPage);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load images';
      setError(new Error(errorMessage));
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProcessedImages();
  }, [page]);

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'File type not supported. Please upload JPEG, PNG, or WebP files.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds ${MAX_FILE_SIZE / 1024 / 1024}MB limit.`;
    }
    return null;
  };

  const handleDrop = useCallback(
    (_droppedFiles: File[], acceptedFiles: File[], rejectedFiles: File[]) => {
      if (rejectedFiles.length > 0) {
        toast.error('Some files were rejected. Please check the file requirements.');
        return;
      }

      const validFiles: ImageFile[] = [];
      const errors: string[] = [];

      acceptedFiles.forEach((file) => {
        const error = validateFile(file);
        if (error) {
          errors.push(`${file.name}: ${error}`);
        } else {
          validFiles.push(Object.assign(file, {
            preview: URL.createObjectURL(file),
          }) as ImageFile);
        }
      });

      if (errors.length > 0) {
        toast.error(errors.join('\n'));
      }

      if (validFiles.length > 0) {
        setFiles((prev) => [...prev, ...validFiles]);
        validFiles.forEach((file) => processImage(file));
      }
    },
    [processImage]
  );

  const handleDelete = async (imageId: string) => {
    try {
      const response = await del<ApiResponse<void>>(`/images/${imageId}`);
      if (!response.success) {
        throw new Error(response.error || 'Failed to delete image');
      }
      setProcessedImages((prev) => prev.filter((img) => img.id !== imageId));
      toast.success('Image deleted successfully');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete image';
      toast.error(errorMessage);
    }
  };

  const handleRetry = async (imageId: string) => {
    const image = processedImages.find((img) => img.id === imageId);
    if (image) {
      try {
        const response = await fetch(image.url);
        if (!response.ok) throw new Error('Failed to fetch image for retry');
        const blob = await response.blob();
        await processImage(new File([blob], image.originalName));
        toast.success('Processing started');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to retry processing';
        toast.error(errorMessage);
      }
    }
  };

  const handleLoadMore = () => {
    setPage((prev) => prev + 1);
  };

  const handleUploadClick = () => {
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  };

  const getStatusBadge = (status: ProcessedImage['status'], imageId: string) => {
    const toneMap: Record<ProcessedImage['status'], 'success' | 'warning' | 'critical'> = {
      completed: 'success',
      processing: 'warning',
      failed: 'critical',
    };

    return (
      <InlineStack gap="200" align="center">
        <Badge tone={toneMap[status]}>{status}</Badge>
        {status === 'failed' && (
          <Button
            variant="plain"
            icon={RefreshMajor}
            onClick={() => handleRetry(imageId)}
            accessibilityLabel="Retry processing"
          />
        )}
      </InlineStack>
    );
  };

  return (
    <BlockStack gap="500">
      {error && (
        <Banner tone="critical" onDismiss={() => setError(null)}>
          <p>{error.message}</p>
        </Banner>
      )}

      <Card>
        <BlockStack gap="500">
          <DropZone
            accept={ALLOWED_TYPES.join(',')}
            type="image"
            onDrop={handleDrop}
            allowMultiple
            label="Drop images here or click to upload"
            errorOverlayText="File type must be JPEG, PNG, or WebP under 5MB"
            overlayText="Drop images to upload"
            customValidator={(file: File) => file.size <= MAX_FILE_SIZE}
          >
            {files.length > 0 && (
              <BlockStack gap="400">
                <div style={{ padding: '20px' }}>
                  <InlineStack gap="300" wrap>
                    {files.map((file) => (
                      <Thumbnail
                        key={file.name}
                        source={file.preview || ''}
                        alt={file.name}
                        size="small"
                      />
                    ))}
                  </InlineStack>
                </div>
              </BlockStack>
            )}
          </DropZone>

          {isUploading && (
            <BlockStack gap="400">
              <Text as="p" variant="bodyMd">Processing images...</Text>
              <ProgressBar 
                progress={Math.round(progress)} 
                size="small" 
                tone="highlight"
              />
            </BlockStack>
          )}
        </BlockStack>
      </Card>

      <Card>
        <BlockStack gap="500">
          <InlineStack gap="500" align="space-between">
            <Text as="h2" variant="headingMd">Processed Images</Text>
            <Button
              onClick={() => fetchProcessedImages()}
              icon={RefreshMajor}
              disabled={isLoading}
              accessibilityLabel="Refresh images"
            >
              Refresh
            </Button>
          </InlineStack>
          
          {isLoading && page === 1 ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '32px' }}>
              <Spinner size="large" />
            </div>
          ) : processedImages.length === 0 ? (
            <EmptyState
              heading="No processed images"
              image="/empty-state-images/no-images.svg"
              action={{
                content: 'Upload images',
                onAction: handleUploadClick,
              }}
            >
              <p>Upload images to start processing them.</p>
            </EmptyState>
          ) : (
            <Grid>
              {processedImages.map((image) => (
                <Grid.Cell columnSpan={{ xs: 6, sm: 4, md: 3, lg: 2 }} key={image.id}>
                  <Card>
                    <BlockStack gap="400">
                      <div
                        style={{ cursor: 'pointer' }}
                        onClick={() => {
                          setSelectedImage(image);
                          setIsModalOpen(true);
                        }}
                      >
                        <Thumbnail source={image.url} alt={image.originalName} />
                      </div>
                      <BlockStack gap="200">
                        <Text as="span" variant="bodyMd" fontWeight="bold">
                          {image.originalName}
                        </Text>
                        {getStatusBadge(image.status, image.id)}
                        <InlineStack gap="200" align="space-between">
                          <Button
                            variant="plain"
                            icon={ViewMajor}
                            onClick={() => {
                              setSelectedImage(image);
                              setIsModalOpen(true);
                            }}
                            accessibilityLabel="View image"
                          />
                          <Button
                            variant="plain"
                            icon={DeleteMajor}
                            onClick={() => handleDelete(image.id)}
                            accessibilityLabel="Delete image"
                            tone="critical"
                          />
                        </InlineStack>
                      </BlockStack>
                    </BlockStack>
                  </Card>
                </Grid.Cell>
              ))}
            </Grid>
          )}

          {hasNextPage && !isLoading && (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <Button onClick={handleLoadMore}>Load more</Button>
            </div>
          )}

          {isLoading && page > 1 && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
              <Spinner size="small" />
            </div>
          )}
        </BlockStack>
      </Card>

      <Modal
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedImage?.originalName || ''}
      >
        <Modal.Section>
          {selectedImage && (
            <BlockStack gap="400">
              <img
                src={selectedImage.processedUrl || selectedImage.url}
                alt={selectedImage.originalName}
                style={{ maxWidth: '100%', height: 'auto' }}
              />
              <BlockStack gap="200">
                <Text as="h3" variant="headingSm">Image Details</Text>
                <Text as="p" variant="bodyMd">
                  Size: {Math.round(selectedImage.metadata.size / 1024)} KB
                </Text>
                <Text as="p" variant="bodyMd">
                  Dimensions: {selectedImage.metadata.width} x {selectedImage.metadata.height}
                </Text>
                <Text as="p" variant="bodyMd">
                  Format: {selectedImage.metadata.format}
                </Text>
                {selectedImage.metadata.processingType && (
                  <Text as="p" variant="bodyMd">
                    Processing: {selectedImage.metadata.processingType.join(', ')}
                  </Text>
                )}
              </BlockStack>
            </BlockStack>
          )}
        </Modal.Section>
      </Modal>
    </BlockStack>
  );
} 