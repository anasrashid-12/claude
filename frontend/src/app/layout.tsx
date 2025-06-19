// frontend/app/layout.tsx
import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Maxflow Image App',
  description: 'Shopify AI Image Processing Dashboard for product images',
  icons: {
    icon: '/favicon.ico', // Optional: Add a favicon in public/
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
      <body className="bg-gray-50 text-gray-900 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
