import './globals.css';
import { ReactNode, Suspense } from 'react';

export const metadata = {
  title: 'Maxflow Image App',
  description: 'AI Image Processing for Shopify',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="description" content={metadata.description} />
        <link rel="icon" href="/favicon.ico" />
        <title>{metadata.title}</title>
      </head>
      <body className="h-full w-full bg-gray-50 text-black dark:bg-black dark:text-white font-sans antialiased overflow-auto">
        <Suspense fallback={<div className="p-4 text-gray-500">Loading...</div>}>
          {children}
        </Suspense>
      </body>
    </html>
  );
}
