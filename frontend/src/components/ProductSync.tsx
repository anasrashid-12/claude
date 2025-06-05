import { useState, useCallback } from 'react';
import {
  Card,
  Button,
  Text,
  BlockStack,
  ResourceList,
  ResourceItem,
  Thumbnail,
  Badge,
  Pagination,
  TextField,
  InlineStack,
  Banner,
  ProgressBar,
  Checkbox
} from '@shopify/polaris';

interface Product {
  id: string;
  title: string;
  images: Array<{
    id: string;
    url: string;
    alt: string;
  }>;
  status: 'synced' | 'pending' | 'processing' | 'failed';
}

export default function ProductSync() {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [syncProgress, setSyncProgress] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchProducts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/products?page=${currentPage}&query=${searchQuery}`);
      if (!response.ok) throw new Error('Failed to fetch products');
      const data = await response.json();
      setProducts(data.products);
    } catch (err) {
      setError('Failed to load products. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, searchQuery]);

  const handleSync = async () => {
    if (selectedProducts.length === 0) return;
    
    setError(null);
    setSyncProgress(0);
    
    try {
      const response = await fetch('/api/products/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productIds: selectedProducts })
      });

      if (!response.ok) throw new Error('Sync failed');

      // Start polling for progress
      const pollProgress = setInterval(async () => {
        const progressResponse = await fetch('/api/products/sync/status');
        const { progress, completed } = await progressResponse.json();
        
        setSyncProgress(progress);
        
        if (completed) {
          clearInterval(pollProgress);
          setSyncProgress(null);
          fetchProducts(); // Refresh product list
        }
      }, 1000);

    } catch (err) {
      setError('Failed to sync products. Please try again.');
      setSyncProgress(null);
    }
  };

  const handleSearch = useCallback((value: string) => {
    setSearchQuery(value);
    setCurrentPage(1);
  }, []);

  const toggleProductSelection = useCallback((productId: string) => {
    setSelectedProducts(prev => 
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  }, []);

  const resourceListMarkup = (
    <ResourceList
      resourceName={{ singular: 'product', plural: 'products' }}
      items={products}
      renderItem={(product) => (
        <ResourceItem
          id={product.id}
          onClick={() => {}}  // Required but no-op since we use checkbox
        >
          <div className="flex items-center gap-4">
            <Checkbox
              label={`Select ${product.title}`}
              labelHidden
              checked={selectedProducts.includes(product.id)}
              onChange={() => toggleProductSelection(product.id)}
            />
            <div className="flex-1">
              <InlineStack gap="400" align="center">
                {product.images[0] && (
                  <Thumbnail
                    source={product.images[0].url}
                    alt={product.images[0].alt}
                  />
                )}
                <div className="flex-1">
                  <Text as="h3" variant="headingMd">{product.title}</Text>
                  <Text as="p" variant="bodySm">
                    {product.images.length} images
                  </Text>
                </div>
                <Badge tone={
                  product.status === 'synced' ? 'success' :
                  product.status === 'failed' ? 'critical' :
                  product.status === 'processing' ? 'attention' :
                  'info'
                }>
                  {product.status}
                </Badge>
              </InlineStack>
            </div>
          </div>
        </ResourceItem>
      )}
    />
  );

  return (
    <Card>
      <BlockStack gap="400">
        <Text as="h2" variant="headingLg">Product Synchronization</Text>
        
        {error && (
          <Banner tone="critical" onDismiss={() => setError(null)}>
            <p>{error}</p>
          </Banner>
        )}

        <InlineStack align="space-between">
          <div className="w-72">
            <TextField
              label="Search products"
              value={searchQuery}
              onChange={handleSearch}
              autoComplete="off"
            />
          </div>
          <Button
            variant="primary"
            onClick={handleSync}
            disabled={selectedProducts.length === 0 || syncProgress !== null}
            loading={syncProgress !== null}
          >
            Sync Selected Products
          </Button>
        </InlineStack>

        {syncProgress !== null && (
          <div className="p-4 bg-slate-50 rounded">
            <Text as="p" variant="bodyMd">Syncing products...</Text>
            <ProgressBar progress={syncProgress} size="small" />
          </div>
        )}

        {resourceListMarkup}

        <div className="flex justify-center">
          <Pagination
            hasPrevious={currentPage > 1}
            hasNext={products.length > 0}
            onPrevious={() => setCurrentPage(p => p - 1)}
            onNext={() => setCurrentPage(p => p + 1)}
          />
        </div>
      </BlockStack>
    </Card>
  );
} 