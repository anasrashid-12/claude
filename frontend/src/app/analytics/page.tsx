import React from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  BlockStack,
  Box,
  DataTable,
  Select
} from '@shopify/polaris';

export default function AnalyticsPage() {
  // Sample data - replace with real data from API
  const processingStats = {
    totalProcessed: 1234,
    averageProcessingTime: '2.3s',
    successRate: '98.5%',
    storageUsed: '45.2 GB',
    costSavings: '$123.45'
  };

  const recentActivity = [
    ['Today', '234', '2.1s', '99%'],
    ['Yesterday', '456', '2.4s', '98%'],
    ['Last 7 days', '1,234', '2.3s', '98.5%'],
    ['Last 30 days', '5,678', '2.2s', '98.7%']
  ];

  const processingTypeStats = [
    ['Background Removal', '789', '3.1s', '97%'],
    ['Optimization', '567', '1.5s', '99%'],
    ['Auto Resize', '345', '1.2s', '100%']
  ];

  return (
    <Page title="Analytics">
      <BlockStack>
        <Layout>
          {/* Stats Overview */}
          <Layout.Section>
            <Card>
              <Box padding="3">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Processing Overview
                  </Text>
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div className="text-center">
                      <Text as="p" variant="headingLg">
                        {processingStats.totalProcessed}
                      </Text>
                      <Text as="p" variant="bodySm">
                        Total Processed
                      </Text>
                    </div>
                    <div className="text-center">
                      <Text as="p" variant="headingLg">
                        {processingStats.averageProcessingTime}
                      </Text>
                      <Text as="p" variant="bodySm">
                        Avg. Processing Time
                      </Text>
                    </div>
                    <div className="text-center">
                      <Text as="p" variant="headingLg">
                        {processingStats.successRate}
                      </Text>
                      <Text as="p" variant="bodySm">
                        Success Rate
                      </Text>
                    </div>
                    <div className="text-center">
                      <Text as="p" variant="headingLg">
                        {processingStats.storageUsed}
                      </Text>
                      <Text as="p" variant="bodySm">
                        Storage Used
                      </Text>
                    </div>
                    <div className="text-center">
                      <Text as="p" variant="headingLg">
                        {processingStats.costSavings}
                      </Text>
                      <Text as="p" variant="bodySm">
                        Estimated Savings
                      </Text>
                    </div>
                  </div>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {/* Recent Activity */}
          <Layout.Section>
            <Card>
              <Box padding="3">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Recent Activity
                  </Text>
                  <DataTable
                    columnContentTypes={['text', 'numeric', 'text', 'text']}
                    headings={['Period', 'Images Processed', 'Avg. Time', 'Success Rate']}
                    rows={recentActivity}
                  />
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {/* Processing Type Stats */}
          <Layout.Section>
            <Card>
              <Box padding="3">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Processing Type Statistics
                  </Text>
                  <DataTable
                    columnContentTypes={['text', 'numeric', 'text', 'text']}
                    headings={['Type', 'Total Images', 'Avg. Time', 'Success Rate']}
                    rows={processingTypeStats}
                  />
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>
        </Layout>
      </BlockStack>
    </Page>
  );
} 