import { useState, useCallback } from 'react';
import {
  Card,
  Text,
  BlockStack,
  ResourceList,
  ResourceItem,
  Thumbnail,
  Button,
  Modal,
  InlineStack,
  Badge,
  Banner
} from '@shopify/polaris';

interface ImageVersion {
  id: string;
  url: string;
  createdAt: string;
  processingType: string;
  metadata: {
    size: string;
    dimensions: string;
    format: string;
  };
  status: 'active' | 'archived';
}

interface ImageHistory {
  id: string;
  originalName: string;
  versions: ImageVersion[];
}

export default function VersionHistory() {
  const [selectedImage, setSelectedImage] = useState<ImageHistory | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [compareVersions, setCompareVersions] = useState<string[]>([]);
  const [images, setImages] = useState<ImageHistory[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchImageHistory = useCallback(async () => {
    try {
      const response = await fetch('/api/images/history');
      if (!response.ok) throw new Error('Failed to fetch image history');
      const data = await response.json();
      setImages(data);
    } catch (err) {
      setError('Failed to load image history');
    }
  }, []);

  const handleRevert = async (imageId: string, versionId: string) => {
    try {
      const response = await fetch('/api/images/revert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imageId, versionId })
      });

      if (!response.ok) throw new Error('Failed to revert image');
      
      // Refresh image history
      fetchImageHistory();
    } catch (err) {
      setError('Failed to revert to selected version');
    }
  };

  const toggleCompareVersion = (versionId: string) => {
    setCompareVersions(prev => {
      if (prev.includes(versionId)) {
        return prev.filter(id => id !== versionId);
      }
      if (prev.length < 2) {
        return [...prev, versionId];
      }
      return [prev[1], versionId];
    });
  };

  const compareModalMarkup = selectedImage && compareMode && (
    <Modal
      open={compareMode}
      onClose={() => {
        setCompareMode(false);
        setCompareVersions([]);
      }}
      title="Compare Versions"
      primaryAction={{
        content: 'Close',
        onAction: () => {
          setCompareMode(false);
          setCompareVersions([]);
        }
      }}
    >
      <Modal.Section>
        <div className="grid grid-cols-2 gap-4">
          {compareVersions.map((versionId, index) => {
            const version = selectedImage.versions.find(v => v.id === versionId);
            if (!version) return null;
            
            return (
              <div key={version.id} className="space-y-2">
                <Text as="h3" variant="headingMd">Version {index + 1}</Text>
                <img
                  src={version.url}
                  alt={`Version ${index + 1}`}
                  className="w-full rounded"
                />
                <BlockStack gap="200">
                  <Text as="p" variant="bodySm">
                    Created: {new Date(version.createdAt).toLocaleString()}
                  </Text>
                  <Text as="p" variant="bodySm">
                    Type: {version.processingType}
                  </Text>
                  <Text as="p" variant="bodySm">
                    Size: {version.metadata.size}
                  </Text>
                </BlockStack>
              </div>
            );
          })}
        </div>
      </Modal.Section>
    </Modal>
  );

  return (
    <Card>
      <BlockStack gap="400">
        <Text as="h2" variant="headingLg">Version History</Text>

        {error && (
          <Banner tone="critical" onDismiss={() => setError(null)}>
            <p>{error}</p>
          </Banner>
        )}

        <ResourceList
          resourceName={{ singular: 'image', plural: 'images' }}
          items={images}
          renderItem={(image) => (
            <ResourceItem
              id={image.id}
              onClick={() => setSelectedImage(image)}
            >
              <BlockStack gap="400">
                <InlineStack gap="400" align="center">
                  <Thumbnail
                    source={image.versions[0]?.url || ''}
                    alt={image.originalName}
                  />
                  <div className="flex-1">
                    <Text as="h3" variant="headingMd">{image.originalName}</Text>
                    <Text as="p" variant="bodySm">
                      {image.versions.length} versions
                    </Text>
                  </div>
                </InlineStack>

                <div className="space-y-4">
                  {image.versions.map((version) => (
                    <div key={version.id} className="flex items-center gap-4 p-2 bg-slate-50 rounded">
                      <Thumbnail
                        source={version.url}
                        alt={`Version of ${image.originalName}`}
                        size="small"
                      />
                      <div className="flex-1">
                        <Text as="p" variant="bodyMd">
                          {version.processingType}
                        </Text>
                        <Text as="p" variant="bodySm">
                          {new Date(version.createdAt).toLocaleString()}
                        </Text>
                      </div>
                      <Badge tone={version.status === 'active' ? 'success' : 'info'}>
                        {version.status}
                      </Badge>
                      <InlineStack gap="200">
                        <Button
                          variant="primary"
                          onClick={() => handleRevert(image.id, version.id)}
                          disabled={version.status === 'active'}
                        >
                          Revert to This
                        </Button>
                        <Button
                          onClick={() => toggleCompareVersion(version.id)}
                          pressed={compareVersions.includes(version.id)}
                          disabled={
                            !compareVersions.includes(version.id) &&
                            compareVersions.length >= 2
                          }
                        >
                          Compare
                        </Button>
                      </InlineStack>
                    </div>
                  ))}
                </div>
              </BlockStack>
            </ResourceItem>
          )}
        />

        {compareVersions.length > 0 && (
          <div className="flex justify-end">
            <Button
              onClick={() => setCompareMode(true)}
              disabled={compareVersions.length < 2}
            >
              Compare Selected Versions
            </Button>
          </div>
        )}

        {compareModalMarkup}
      </BlockStack>
    </Card>
  );
} 