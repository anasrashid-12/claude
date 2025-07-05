// src/app/layout.tsx
import './globals.css';
import { ReactNode, Suspense } from 'react';

export const metadata = {
  title: 'Maxflow Image App',
  description: 'AI Image Processing for Shopify',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <title>{metadata.title}</title>
        <meta name="description" content={metadata.description} />
      </head>
      <body className="bg-gray-50 text-black">
        <Suspense fallback={<div className="p-4">Loading...</div>}>
          {children}
        </Suspense>
      </body>
    </html>
  );
}
