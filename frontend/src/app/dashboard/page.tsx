'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useShop from '@/hooks/useShop';
import ClientLayout from '../../../components/ClientLayout';
import ImageGallery from '../../../components/ImageGallery';

export default function DashboardPage() {
  const router = useRouter();
  const { shop, loading } = useShop();

  useEffect(() => {
    if (!loading && !shop) {
      router.push('/login');
    }
  }, [loading, shop, router]);

  if (loading) {
    return <p className="p-4 text-gray-500">Loading dashboard...</p>;
  }

  if (!shop) return null;

  return (
    <ClientLayout>
      <div className="max-w-6xl mx-auto p-4">
        <header className="mb-6">
          <h1 className="text-2xl font-bold">🖼️ Image Gallery</h1>
          <p className="text-gray-600 text-sm">
            View all your AI-processed images below.
          </p>
        </header>

        <section>
          <ImageGallery shop={shop} />
        </section>
      </div>
    </ClientLayout>
  );
}
