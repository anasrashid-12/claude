'use client';

import useShop from '@/hooks/useShop';
import ClientLayout from '@/components/ClientLayout';
import ImageGallery from '@/components/ImageGallery';

export default function DashboardClient() {
  const { shop, loading } = useShop();

  if (loading) {
    return (
      <ClientLayout>
        <div className="p-6 text-gray-500">Loading dashboard...</div>
      </ClientLayout>
    );
  }

  if (!shop) {
    return (
      <ClientLayout>
        <div className="p-6">
          <p className="text-red-500 font-medium">
            ❌ Unauthorized. Please open the app from your Shopify Admin.
          </p>
        </div>
      </ClientLayout>
    );
  }

  return (
    <ClientLayout>
      <div className="max-w-6xl mx-auto px-6 py-4 space-y-4">
        <header>
          <h1 className="text-2xl font-bold text-gray-800">🖼️ Image Gallery</h1>
          <p className="text-gray-600 text-sm">Browse all your AI-processed images below.</p>
        </header>
        <ImageGallery shop={shop} />
      </div>
    </ClientLayout>
  );
}
