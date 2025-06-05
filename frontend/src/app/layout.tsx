// app/layout.tsx
'use client';

import './globals.css';
import { AppProvider } from '@shopify/polaris';
import '@shopify/polaris/build/esm/styles.css';
import { Toaster } from 'react-hot-toast';
import { ShopifyProvider } from './providers/ShopifyProvider';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://unpkg.com/@shopify/polaris@12.0.0/build/esm/styles.css"
        />
      </head>
      <body className="app-root" suppressHydrationWarning>
        <ShopifyProvider>
          <AppProvider i18n={{
            Polaris: {
              Common: {
                loading: 'Loading...'
              }
            }
          }}>
            {children}
            <Toaster position="top-right" />
          </AppProvider>
        </ShopifyProvider>
      </body>
    </html>
  );
}
