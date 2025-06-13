'use client';

import { AppProvider } from '@shopify/polaris';
import '@shopify/polaris/build/esm/styles.css';
import en from '@shopify/polaris/locales/en.json'; // ✅ Corrected line

export function PolarisProvider({ children }: { children: React.ReactNode }) {
  return <AppProvider i18n={en}>{children}</AppProvider>;
}
