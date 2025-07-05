'use client';

import { ReactNode, Suspense } from 'react';
import AppBridgeProvider from '@/components/AppBridgeProvider';
import ClientLayout from '@/components/ClientLayout';
import Sidebar from './sidebar';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AppBridgeProvider>
      <ClientLayout>
        <div className="flex min-h-screen bg-gray-50">
          <aside className="w-64 border-r bg-white">
            <Suspense fallback={<div className="p-6 text-gray-500">Loading menu...</div>}>
              <Sidebar />
            </Suspense>
          </aside>
          <main className="flex-1 overflow-y-auto px-6 py-4">{children}</main>
        </div>
      </ClientLayout>
    </AppBridgeProvider>
  );
}
