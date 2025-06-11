import React from 'react';
import { SkeletonPage, Layout, Card, SkeletonBodyText, Box } from '@shopify/polaris';
import { UI } from '../constants';

export const LoadingState: React.FC = () => {
  return (
    <SkeletonPage>
      <Layout>
        <Layout.Section>
          <Card>
            <Box padding={UI.SPACING.TIGHT}>
              <SkeletonBodyText lines={1} />
            </Box>
            <Box padding={UI.SPACING.TIGHT}>
              <SkeletonBodyText lines={5} />
            </Box>
          </Card>
        </Layout.Section>
        <Layout.Section>
          <Card>
            <Box padding={UI.SPACING.TIGHT}>
              <SkeletonBodyText lines={1} />
            </Box>
            <Box padding={UI.SPACING.TIGHT}>
              <SkeletonBodyText lines={3} />
            </Box>
          </Card>
        </Layout.Section>
      </Layout>
    </SkeletonPage>
  );
}; 