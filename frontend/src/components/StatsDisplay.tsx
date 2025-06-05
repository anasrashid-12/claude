import { Card, TextStyle } from '@shopify/polaris';
import { ProcessingStats } from '../types/stats';

interface StatsDisplayProps {
  stats: ProcessingStats;
}

export function StatsDisplay({ stats }: StatsDisplayProps) {
  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat().format(Math.round(num));
  };

  const formatBytes = (bytes: number): string => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }

    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  return (
    <Card title="Processing Statistics">
      <Card.Section>
        <div style={{ marginBottom: '1rem' }}>
          <TextStyle variation="strong">Total Processed</TextStyle>
          <div>{formatNumber(stats.total_processed)} images</div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <TextStyle variation="strong">Success Rate</TextStyle>
          <div>{(stats.success_rate * 100).toFixed(1)}%</div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <TextStyle variation="strong">Average Processing Time</TextStyle>
          <div>{stats.average_processing_time.toFixed(1)} seconds</div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <TextStyle variation="strong">Storage Used</TextStyle>
          <div>{formatBytes(stats.total_storage_used)}</div>
        </div>

        <div>
          <TextStyle variation="strong">Processing Rate</TextStyle>
          <div>{stats.images_per_hour.toFixed(1)} images/hour</div>
        </div>
      </Card.Section>
    </Card>
  );
} 