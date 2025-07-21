'use client';

import { Card } from '@shopify/polaris';
import { cn } from '../../utils/utils';

export default function ThemedCard({
  children,
  padding = '400',
  className = '',
}: {
  children: React.ReactNode;
  padding?: '200' | '400' | '600';
  className?: string;
}) {
  return (
    <div className={cn('bg-white dark:bg-gray-900 rounded-lg shadow-sm p-1', className)}>
      <Card padding={padding}>{children}</Card>
    </div>
  );
}
