'use client';
import Link from 'next/link';
import { Page, Layout, Card, Text, InlineStack, Button } from '@shopify/polaris';

export default function DashboardPage() {
  return (
    <Page title="Dashboard">
      <Layout>
        <Layout.Section>
          <Card>
            <InlineStack gap="400">
              <Button url="/dashboard/image-gallery">Image Gallery</Button>
              <Button url="/dashboard/processing-queue">Processing Queue</Button>
              <Button url="/dashboard/settings">Settings</Button>
            </InlineStack>
            <Text variant="bodyMd" as="p" tone="subdued" alignment="center">
              Welcome to Maxflow AI Image Processing App
            </Text>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
