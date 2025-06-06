'use client';

import React from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  ProgressBar,
  Button,
  DataTable,
  BlockStack,
  Box,
  InlineStack
} from '@shopify/polaris';
import { ImageMajor } from '@shopify/polaris-icons';

export default function DashboardPage() {
  // Sample data - replace with real data from API
  const stats = {
    totalProcessed: 1234,
    inQueue: 5,
    failedJobs: 2,
    storageUsed: '45.2 GB',
  };

  const recentJobs = [
    ['Product A', 'Background Removal', 'Completed', '2 mins ago'],
    ['Product B', 'Optimization', 'Processing', '5 mins ago'],
    ['Product C', 'Bulk Process', 'Failed', '10 mins ago'],
  ];

  return (
    <Page title="Dashboard">
      <BlockStack gap="500">
        {/* Stats Overview */}
        <Layout>
          <Layout.Section>
            <Card>
              <Box padding="400">
                <BlockStack gap="400">
                  <InlineStack gap="400" align="space-between">
                    <Box padding="400" width="25%">
                      <BlockStack gap="200" align="center">
                        <Text as="h3" variant="headingMd">Total Processed</Text>
                        <Text as="p" variant="heading2xl">{stats.totalProcessed}</Text>
                      </BlockStack>
                    </Box>
                    <Box padding="400" width="25%">
                      <BlockStack gap="200" align="center">
                        <Text as="h3" variant="headingMd">In Queue</Text>
                        <Text as="p" variant="heading2xl">{stats.inQueue}</Text>
                      </BlockStack>
                    </Box>
                    <Box padding="400" width="25%">
                      <BlockStack gap="200" align="center">
                        <Text as="h3" variant="headingMd">Failed Jobs</Text>
                        <Text as="p" variant="heading2xl">{stats.failedJobs}</Text>
                      </BlockStack>
                    </Box>
                    <Box padding="400" width="25%">
                      <BlockStack gap="200" align="center">
                        <Text as="h3" variant="headingMd">Storage Used</Text>
                        <Text as="p" variant="heading2xl">{stats.storageUsed}</Text>
                      </BlockStack>
                    </Box>
                  </InlineStack>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {/* Processing Queue */}
          <Layout.Section>
            <Card>
              <Box padding="400">
                <BlockStack gap="400">
                  <InlineStack align="space-between">
                    <Text as="h3" variant="headingMd">Current Progress</Text>
                    <Button>View All</Button>
                  </InlineStack>
                  <ProgressBar progress={75} size="small" />
                  <Text as="p" variant="bodySm" tone="subdued">
                    3 of 4 images processed
                  </Text>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {/* Recent Jobs */}
          <Layout.Section>
            <Card>
              <Box padding="400">
                <BlockStack gap="400">
                  <Text as="h3" variant="headingMd">Recent Jobs</Text>
                  <DataTable
                    columnContentTypes={['text', 'text', 'text', 'text']}
                    headings={['Product', 'Process Type', 'Status', 'Time']}
                    rows={recentJobs}
                  />
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {/* Quick Actions */}
          <Layout.Section variant="oneThird">
            <Card>
              <Box padding="400">
                <BlockStack gap="400">
                  <Text as="h3" variant="headingMd">Quick Actions</Text>
                  <BlockStack gap="300">
                    <Button variant="primary" icon={ImageMajor}>
                      Process New Image
                    </Button>
                    <Button>View Gallery</Button>
                    <Button>Settings</Button>
                  </BlockStack>
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>
        </Layout>
      </BlockStack>
    </Page>
  );
} 