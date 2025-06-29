import { Suspense } from 'react';
import Sidebar from './sidebar';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Suspense fallback={<div className="p-6">Loading menu...</div>}>
        <Sidebar />
      </Suspense>
      <main className="flex-1 p-6 overflow-y-auto">{children}</main>
    </div>
  );
}
