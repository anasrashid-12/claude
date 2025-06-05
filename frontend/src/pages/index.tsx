import { useCallback, useState } from 'react';
import { Page, Layout, Card, Button, Banner } from '@shopify/polaris';
import { ImageUploader } from '../components/ImageUploader';
import { ProcessingQueue } from '../components/ProcessingQueue';
import { StatsDisplay } from '../components/StatsDisplay';
import { useImageProcessing } from '../hooks/useImageProcessing';
import { useQueue } from '../hooks/useQueue';
import { useStats } from '../hooks/useStats';

export default function HomePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { processImage, isProcessing, error } = useImageProcessing();
  const { queueStatus } = useQueue();
  const { processingStats } = useStats();

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
  }, []);

  const handleProcess = useCallback(async () => {
    if (selectedFile) {
      await processImage(selectedFile);
      setSelectedFile(null);
    }
  }, [selectedFile, processImage]);

  return (
    <Page title="AI Image Processing">
      <Layout>
        {error && (
          <Layout.Section>
            <Banner status="critical">
              {error}
            </Banner>
          </Layout.Section>
        )}

        <Layout.Section>
          <Card sectioned>
            <ImageUploader
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
            />
            <div style={{ marginTop: '1rem' }}>
              <Button
                primary
                loading={isProcessing}
                disabled={!selectedFile || isProcessing}
                onClick={handleProcess}
              >
                Process Image
              </Button>
            </div>
          </Card>
        </Layout.Section>

        <Layout.Section secondary>
          <StatsDisplay stats={processingStats} />
        </Layout.Section>

        <Layout.Section>
          <ProcessingQueue status={queueStatus} />
        </Layout.Section>
      </Layout>
    </Page>
  );
} 