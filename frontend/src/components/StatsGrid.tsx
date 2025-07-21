'use client';

import { ImageIcon, LoaderIcon, CheckCircleIcon, AlertCircleIcon } from 'lucide-react';
import StatCard from './StatCard';

interface StatsGridProps {
  total: number;
  processing: number;
  failed: number;
  completed: number;
}

export default function StatsGrid({ total, processing, failed, completed }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard title="Total Images" value={total} icon={ImageIcon} />
      <StatCard title="Processing" value={processing} icon={LoaderIcon} />
      <StatCard title="Completed" value={completed} icon={CheckCircleIcon} />
      <StatCard title="Failed" value={failed} icon={AlertCircleIcon} />
    </div>
  );
}
