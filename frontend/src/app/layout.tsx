import './globals.css';
import { ReactNode } from 'react';
import AppBridgeProvider from '../components/AppBridgeProvider';
import PolarisProvider from '../components/PolarisProvider';

export const metadata = {
  title: 'Maxflow Image App',
  description: 'AI Image Processing for Shopify',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-black">
        <AppBridgeProvider>
          <PolarisProvider>{children}</PolarisProvider>
        </AppBridgeProvider>
      </body>
    </html>
  );
}
