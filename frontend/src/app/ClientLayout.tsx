'use client';

import { ReactNode } from 'react';
import { AppProvider } from '@shopify/polaris';
import { ShopifyProvider } from './providers/ShopifyProvider';
import enTranslations from '@shopify/polaris/locales/en.json';

interface ClientLayoutProps {
  children: ReactNode;
}

export default function ClientLayout({ children }: ClientLayoutProps) {
  return (
    <AppProvider i18n={enTranslations}>
      <ShopifyProvider>
        {children}
      </ShopifyProvider>
    </AppProvider>
  );
} 