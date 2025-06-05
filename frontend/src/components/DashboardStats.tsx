import React, { useState } from 'react';
import {
  Card,
  Layout,
  TextContainer,
  Text,
  Icon,
  Box,
  Banner,
  Button,
  Spinner,
  InlineStack,
} from '@shopify/polaris';
import {
  CircleTickMajor,
  ClockMajor,
  AlertMinor,
  ImageMajor,
  RefreshMinor,
} from '@shopify/polaris-icons';
import { useProcessingStats } from '../utils/hooks';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  loading?: boolean;
  subtitle?: string;
}> = ({ title, value, icon, trend, loading, subtitle }) => (
  <Card>
    <Box padding="400">
      <Box>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {icon}
          <TextContainer spacing="tight">
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Spinner size="small" />
                <Text variant="headingMd" as="h3">Loading...</Text>
              </div>
            ) : (
              <Text variant="headingMd" as="h3">{value}</Text>
            )}
            <Text variant="bodySm" as="p" tone="subdued">
              {title}
            </Text>
            {subtitle && (
              <Text variant="bodySm" as="p" tone="subdued">
                {subtitle}
              </Text>
            )}
            {trend !== undefined && (
              <Text
                variant="bodySm"
                as="p"
                tone={trend >= 0 ? 'success' : 'critical'}
              >
                {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
              </Text>
            )}
          </TextContainer>
        </div>
      </Box>
    </Box>
  </Card>
);

export const DashboardStats: React.FC = () => {
  const { data: stats, isLoading, error, refetch } = useProcessingStats();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
  };

  return (
    <Layout>
      <Layout.Section>
        {error && (
          <Banner tone="critical">
            <p>Failed to load statistics: {error.message}</p>
          </Banner>
        )}

        <Box padding="400">
          <InlineStack align="space-between" blockAlign="center">
            <Text variant="headingLg" as="h2">Processing Statistics</Text>
            <Button
              icon={<Icon source={RefreshMinor} />}
              onClick={handleRefresh}
              disabled={isLoading || isRefreshing}
              loading={isRefreshing}
            >
              Refresh
            </Button>
          </InlineStack>

          <Box paddingBlockStart="400">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
              <StatCard
                title="Total Processed"
                value={stats?.totalProcessed || 0}
                icon={<Icon source={CircleTickMajor} tone="success" />}
                loading={isLoading}
              />
              <StatCard
                title="In Queue"
                value={stats?.inQueue || 0}
                icon={<Icon source={ClockMajor} tone="warning" />}
                loading={isLoading}
              />
              <StatCard
                title="Failed Jobs"
                value={stats?.failedJobs || 0}
                icon={<Icon source={AlertMinor} tone="critical" />}
                loading={isLoading}
              />
              <StatCard
                title="Success Rate"
                value={`${stats?.successRate || 0}%`}
                icon={<Icon source={ImageMajor} tone="emphasis" />}
                subtitle={`Avg. Time: ${stats?.averageProcessingTime || '0s'}`}
                loading={isLoading}
              />
            </div>
          </Box>
        </Box>
      </Layout.Section>
    </Layout>
  );
};

export default DashboardStats; 