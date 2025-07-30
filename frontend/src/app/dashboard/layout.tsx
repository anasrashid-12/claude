// components/DashboardLayout.tsx
'use client';

import { ReactNode, Suspense, useState } from 'react';
import AppBridgeProvider from '@/components/AppBridgeProvider';
import { AppProvider, Frame } from '@shopify/polaris';
import en from '@shopify/polaris/locales/en.json';
import { ThemeProvider, useTheme } from '@/components/ThemeProvider';
import Sidebar from './sidebar';
import TopBar from '@/components/TopBar';
import '@shopify/polaris/build/esm/styles.css';

function InnerLayout({ children }: { children: ReactNode }) {
  const { theme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <AppProvider i18n={en} theme={theme === 'dark' ? 'dark-experimental' : 'light'}>
      <Frame>
        <div className="flex min-h-screen w-full bg-gray-50 dark:bg-[#0e1320] text-gray-900 dark:text-white">
          {/* Overlay */}
          {sidebarOpen && (
            <div
              className="fixed inset-0 z-30 bg-black bg-opacity-40 md:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Sidebar */}
          <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          {/* Main Content */}
          <div className="flex flex-col flex-1 overflow-hidden">
            <TopBar onMenuClick={() => setSidebarOpen(true)} />
            <main className="flex-1 overflow-y-auto p-4 sm:p-6">
              <Suspense fallback={<p className="text-center text-gray-500 dark:text-gray-400">Loading...</p>}>
                {children}
              </Suspense>
            </main>
          </div>
        </div>
      </Frame>
    </AppProvider>
  );
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AppBridgeProvider>
      <ThemeProvider>
        <InnerLayout>{children}</InnerLayout>
      </ThemeProvider>
    </AppBridgeProvider>
  );
}
