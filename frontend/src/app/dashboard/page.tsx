import { Suspense } from 'react';
import DashboardClient from './dashboard-client';

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="p-6 text-gray-500">Loading dashboard...</div>}>
      <DashboardClient />
    </Suspense>
  );
}
