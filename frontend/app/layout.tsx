import '../styles/globals.css'
import { Providers } from './providers/providers';

export const metadata = {
  title: 'AI Image Processor',
  description: 'Process images with AI inside your Shopify store',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
