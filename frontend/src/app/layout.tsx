import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Maxflow Image App',
  description: 'Shopify AI Image Processing App for background removal and enhancements',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  );
}
