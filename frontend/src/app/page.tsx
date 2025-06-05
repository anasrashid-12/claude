// src/app/page.tsx
'use client';

import { 
  Page, 
  Layout, 
  Tabs, 
  Frame, 
  Loading, 
  Banner,
  Card,
  BlockStack,
  Text
} from '@shopify/polaris';
import { useState, useCallback, Suspense } from 'react';
import DashboardStats from '../components/DashboardStats';
import ImageGallery from '../components/ImageGallery';
import ProcessingQueue from '../components/ProcessingQueue';
import ProductSync from '../components/ProductSync';
import VersionHistory from '../components/VersionHistory';
import ProcessingSettings from '../components/ProcessingSettings';

export default function HomePage() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const tabs = [
    {
      id: 'dashboard',
      content: 'Dashboard',
      accessibilityLabel: 'Dashboard',
      panelID: 'dashboard-content',
    },
    {
      id: 'products',
      content: 'Products',
      accessibilityLabel: 'Product Synchronization',
      panelID: 'products-content',
    },
    {
      id: 'history',
      content: 'Version History',
      accessibilityLabel: 'Version History',
      panelID: 'history-content',
    },
    {
      id: 'settings',
      content: 'Settings',
      accessibilityLabel: 'Processing Settings',
      panelID: 'settings-content',
    },
  ];

  const handleTabChange = useCallback(
    async (selectedTabIndex: number) => {
      try {
        setIsLoading(true);
        setError(null);
        setSelectedTab(selectedTabIndex);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred while changing tabs');
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const renderTabContent = () => {
    switch (selectedTab) {
      case 0:
        return (
          <Layout>
            <Layout.Section>
              <DashboardStats />
            </Layout.Section>
            
            <Layout.Section>
              <Card>
                <ImageGallery />
              </Card>
            </Layout.Section>

            <Layout.Section variant="oneThird">
              <Card>
                <BlockStack gap="400">
                  <Text as="h2" variant="headingMd">Processing Queue</Text>
                  <ProcessingQueue />
                </BlockStack>
              </Card>
            </Layout.Section>
          </Layout>
        );
      case 1:
        return (
          <Layout.Section>
            <ProductSync />
          </Layout.Section>
        );
      case 2:
        return (
          <Layout.Section>
            <VersionHistory />
          </Layout.Section>
        );
      case 3:
        return (
          <Layout.Section>
            <ProcessingSettings />
          </Layout.Section>
        );
      default:
        return null;
    }
  };

  return (
    <Frame>
      {isLoading && <Loading />}
      <Page title="AI Image Processing">
        <Layout>
          <Layout.Section>
            {error && (
              <Banner tone="critical" onDismiss={() => setError(null)}>
                <p>{error}</p>
              </Banner>
            )}
            
            <Tabs tabs={tabs} selected={selectedTab} onSelect={handleTabChange} />
            
            <Suspense fallback={<Loading />}>
              {renderTabContent()}
            </Suspense>
          </Layout.Section>
        </Layout>
      </Page>
    </Frame>
  );
}
