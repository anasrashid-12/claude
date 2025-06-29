'use client';

import useShop from '@/hooks/useShop';
import ClientLayout from '../../components/ClientLayout';
import ImageGallery from '../../components/ImageGallery';

export default function DashboardClient() {
  const { shop, loading } = useShop();

  if (loading) return <p className="p-4 text-gray-500">Loading dashboard...</p>;

  if (!shop) {
    return (
      <div className="p-4">
        <p className="text-red-500">❌ Unauthorized. Please open app from Shopify admin.</p>
      </div>
    );
  }

  return (
    <ClientLayout>
      <div className="max-w-6xl mx-auto p-4">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">🖼️ Image Gallery</h1>
          <p className="text-gray-600 text-sm">View all your AI-processed images below.</p>
        </header>
        <ImageGallery shop={shop} />
      </div>
    </ClientLayout>
  );
}
