'use client';

import { AppProvider } from '@shopify/polaris';
import '@shopify/polaris/build/esm/styles.css';
import en from '@shopify/polaris/locales/en.json';

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppProvider i18n={en}>
      <div className="max-w-7xl mx-auto p-4">{children}</div>
    </AppProvider>
  );
}
