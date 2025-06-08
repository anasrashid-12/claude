import React, { useState, useEffect } from 'react';
import {
  Card,
  Grid,
  Text,
  Button,
  Icon,
  Spinner,
} from '@shopify/polaris';
import {
  ImageMajor,
  ClockMajor,
  AnalyticsMajor,
  StorageMajor,
} from '@shopify/polaris-icons';

interface ProcessingStats {
  totalProcessed: number;
  successRate: number;
  averageProcessingTime: number;
  totalStorageUsed: number;
  imagesPerHour: number;
}

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  loading?: boolean;
  subtitle?: string;
}> = ({ title, value, icon, trend, loading, subtitle }) => (
  <Card>
    <div className="stat-card">
      <div className="stat-header">
        <Text as="h3" variant="headingSm">{title}</Text>
        <Icon source={icon} />
      </div>
      <div className="stat-content">
        {loading ? (
          <Spinner size="small" />
        ) : (
          <>
            <Text as="p" variant="heading2xl">{value}</Text>
            {subtitle && (
              <Text as="p" variant="bodySm" tone="subdued">
                {subtitle}
              </Text>
            )}
            {trend !== undefined && (
              <Text
                as="p"
                variant="bodySm"
                tone={trend >= 0 ? 'success' : 'critical'}
              >
                {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
              </Text>
            )}
          </>
        )}
      </div>
    </div>
  </Card>
);

export const DashboardStats: React.FC = () => {
  const [stats, setStats] = useState<ProcessingStats | null>(null);
  const [loading, setLoading] = useState(true);

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/stats/processing');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleRefresh();
  }, []);

  const formatStorageSize = (bytes: number): string => {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    let size = bytes;
    while (size >= 1024 && i < sizes.length - 1) {
      size /= 1024;
      i++;
    }
    return `${size.toFixed(1)} ${sizes[i]}`;
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    return `${(seconds / 60).toFixed(1)}m`;
  };

  return (
    <div className="dashboard-stats">
      <div className="stats-header">
        <Text as="h2" variant="headingLg">Processing Statistics</Text>
        <Button onClick={handleRefresh} loading={loading}>
          Refresh
        </Button>
      </div>

      <Grid>
        <Grid.Cell columnSpan={{ xs: 6, sm: 3, md: 3, lg: 3 }}>
          <StatCard
            title="Total Processed"
            value={stats?.totalProcessed || 0}
            icon={ImageMajor}
            loading={loading}
          />
        </Grid.Cell>

        <Grid.Cell columnSpan={{ xs: 6, sm: 3, md: 3, lg: 3 }}>
          <StatCard
            title="Success Rate"
            value={`${stats?.successRate.toFixed(1)}%` || '0%'}
            icon={AnalyticsMajor}
            loading={loading}
            trend={stats?.successRate ? stats.successRate - 100 : 0}
          />
        </Grid.Cell>

        <Grid.Cell columnSpan={{ xs: 6, sm: 3, md: 3, lg: 3 }}>
          <StatCard
            title="Avg. Processing Time"
            value={stats ? formatTime(stats.averageProcessingTime) : '0s'}
            icon={ClockMajor}
            loading={loading}
            subtitle="per image"
          />
        </Grid.Cell>

        <Grid.Cell columnSpan={{ xs: 6, sm: 3, md: 3, lg: 3 }}>
          <StatCard
            title="Storage Used"
            value={stats ? formatStorageSize(stats.totalStorageUsed) : '0 B'}
            icon={StorageMajor}
            loading={loading}
          />
        </Grid.Cell>
      </Grid>

      <style jsx>{`
        .dashboard-stats {
          padding: 20px;
        }
        .stats-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }
        .stat-card {
          padding: 16px;
        }
        .stat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }
        .stat-content {
          text-align: center;
        }
      `}</style>
    </div>
  );
};

export default DashboardStats; 