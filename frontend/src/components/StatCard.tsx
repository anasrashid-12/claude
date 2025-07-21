'use client';

import { Card, CardContent } from '../components/ui/card';
import { cn } from '../../lib/utils';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  title: string;
  value: string | number;
  description?: string;
  className?: string;
}

export default function StatCard({
  icon: Icon,
  title,
  value,
  description,
  className,
}: StatCardProps) {
  return (
    <Card
      className={cn(
        'p-4 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900',
        className
      )}
    >
      <CardContent className="flex items-center gap-3 p-0">
        <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 flex-shrink-0">
          <Icon className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <span className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{title}</span>
          <span className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{value}</span>
          {description && (
            <span className="text-xs text-gray-400 dark:text-gray-500">{description}</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
