'use client';
import { Page, Layout } from '@shopify/polaris';
import ProcessingQueue from '../../../components/ProcessingQueue';

export default function ProcessingQueuePage() {
  return (
    <Page title="Processing Queue">
      <Layout>
        <Layout.Section>
          <ProcessingQueue />
        </Layout.Section>
      </Layout>
    </Page>
  );
}
