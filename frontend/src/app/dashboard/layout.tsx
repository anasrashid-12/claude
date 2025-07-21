'use client';

import { ReactNode, Suspense } from 'react';
import AppBridgeProvider from '@/components/AppBridgeProvider';
import { AppProvider, Frame } from '@shopify/polaris';
import en from '@shopify/polaris/locales/en.json';
import { ThemeProvider, useTheme } from '@/components/ThemeProvider';
import Sidebar from './sidebar';
import TopBar from '@/components/TopBar';
import '@shopify/polaris/build/esm/styles.css';

function InnerLayout({ children }: { children: ReactNode }) {
  const { theme } = useTheme();

  return (
    <AppProvider i18n={en} theme={theme === 'dark' ? 'dark-experimental' : 'light'}>
      <Frame>
        <div className="flex min-h-screen w-full overflow-hidden bg-gray-50 dark:bg-[#0e1320] text-gray-900 dark:text-white">
          <Sidebar />
          <div className="flex flex-col flex-1 overflow-hidden">
            <TopBar />
            <main className="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50 dark:bg-[#0e1320]">
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
