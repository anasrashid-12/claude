import { useState, useEffect, useCallback } from 'react';
import {
  Page,
  Layout,
  Card,
  ResourceList,
  Thumbnail,
  Text,
  Button,
  Badge,
  Modal,
  Select,
  Box,
  Banner,
  Spinner,
  EmptyState,
  BlockStack,
  InlineStack,
  Frame,
  Toast,
} from '@shopify/polaris';
import { useAuthenticatedFetch } from '../hooks/useAuthenticatedFetch';

interface Product {
  id: string;
  title: string;
  image: {
    src: string;
    alt: string;
  };
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export function ImageProcessingDashboard() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [modalActive, setModalActive] = useState(false);
  const [processingType, setProcessingType] = useState('background_removal');
  const [toastProps, setToastProps] = useState<{ content: string; error?: boolean } | null>(null);
  const fetch = useAuthenticatedFetch();

  useEffect(() => {
    fetchProducts();
  }, []);

  const showToast = useCallback((content: string, error = false) => {
    setToastProps({ content, error });
  }, []);

  const dismissToast = useCallback(() => {
    setToastProps(null);
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/v1/products');
      if (!response?.ok) {
        throw new Error('Failed to fetch products');
      }
      const data = await response.json();
      setProducts(data.products);
    } catch (err) {
      showToast('Failed to load products', true);
      console.error('Error fetching products:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProcessImages = async () => {
    if (selectedProducts.length === 0) {
      showToast('Please select at least one product', true);
      return;
    }

    setIsProcessing(true);
    try {
      const response = await fetch('/api/v1/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_ids: selectedProducts,
          process_type: processingType,
        }),
      });

      if (!response?.ok) {
        throw new Error('Failed to start processing');
      }

      showToast('Processing started successfully');
      setModalActive(false);
      
      // Update products status
      setProducts(prevProducts =>
        prevProducts.map(product =>
          selectedProducts.includes(product.id)
            ? { ...product, status: 'processing' }
            : product
        )
      );
    } catch (err) {
      showToast('Failed to start processing', true);
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const processingOptions = [
    { label: 'Background Removal', value: 'background_removal' },
    { label: 'Image Enhancement', value: 'enhancement' },
    { label: 'Format Conversion', value: 'format_conversion' },
  ];

  const resourceName = {
    singular: 'product',
    plural: 'products',
  };

  const bulkActions = [
    {
      content: 'Process Selected Images',
      onAction: () => setModalActive(true),
    },
  ];

  if (isLoading) {
    return (
      <Frame>
        <Page title="AI Image Processing">
          <Layout>
            <Layout.Section>
              <Card>
                <div style={{ padding: '16px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                  <Spinner size="large" />
                </div>
              </Card>
            </Layout.Section>
          </Layout>
        </Page>
      </Frame>
    );
  }

  if (products.length === 0) {
    return (
      <Frame>
        <Page title="AI Image Processing">
          <Layout>
            <Layout.Section>
              <Card>
                <EmptyState
                  heading="No products found"
                  image="/empty-state.svg"
                >
                  <p>Add products to your store to start processing images.</p>
                </EmptyState>
              </Card>
            </Layout.Section>
          </Layout>
          {toastProps && (
            <Toast
              content={toastProps.content}
              error={toastProps.error}
              onDismiss={dismissToast}
            />
          )}
        </Page>
      </Frame>
    );
  }

  const handleSelectionChange = (selectedItems: string | string[]) => {
    setSelectedProducts(Array.isArray(selectedItems) ? selectedItems : [selectedItems]);
  };

  return (
    <Frame>
      <Page title="AI Image Processing">
        <Layout>
          <Layout.Section>
            <Card>
              <ResourceList
                resourceName={resourceName}
                items={products}
                selectedItems={selectedProducts}
                onSelectionChange={handleSelectionChange}
                selectable
                bulkActions={bulkActions}
                renderItem={(item: Product) => {
                  const { id, title, image, status } = item;
                  const tone = {
                    pending: 'info',
                    processing: 'warning',
                    completed: 'success',
                    failed: 'critical',
                  } as const;

                  return (
                    <ResourceList.Item
                      id={id}
                      accessibilityLabel={`View details for ${title}`}
                      onClick={() => {}}
                    >
                      <div style={{ padding: '16px' }}>
                        <InlineStack align="space-between">
                          <InlineStack align="start" gap="400">
                            <Thumbnail source={image.src} alt={image.alt} />
                            <Text as="span" variant="bodyMd" fontWeight="bold">
                              {title}
                            </Text>
                          </InlineStack>
                          <Badge tone={tone[status]}>{status}</Badge>
                        </InlineStack>
                      </div>
                    </ResourceList.Item>
                  );
                }}
              />
            </Card>
          </Layout.Section>

          <Modal
            open={modalActive}
            onClose={() => setModalActive(false)}
            title="Process Images"
            primaryAction={{
              content: 'Start Processing',
              onAction: handleProcessImages,
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
              <BlockStack gap="400">
                <Select
                  label="Processing Type"
                  options={processingOptions}
                  onChange={setProcessingType}
                  value={processingType}
                />
                <Banner tone="info">
                  Selected products: {selectedProducts.length}
                </Banner>
              </BlockStack>
            </Modal.Section>
          </Modal>
          {toastProps && (
            <Toast
              content={toastProps.content}
              error={toastProps.error}
              onDismiss={dismissToast}
            />
          )}
        </Layout>
      </Page>
    </Frame>
  );
} 