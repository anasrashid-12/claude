'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useShop from '../../hooks/useShop';
import UploadSection from '../../../components/UploadSection';
import ImageGallery from '../../../components/ImageGallery';
import ClientLayout from '../../../components/ClientLayout';

export default function DashboardPage() {
  const router = useRouter();
  const { shop, loading } = useShop();

  useEffect(() => {
    if (!loading && !shop) {
      router.push('/');
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
          <h1 className="text-2xl font-bold">📊 Maxflow Dashboard</h1>
          <p className="text-gray-600 text-sm">
            Welcome! Upload and manage your AI-processed product images.
          </p>
        </header>

        <section className="mb-10">
          <UploadSection shop={shop} />
        </section>

        <section>
          <ImageGallery shop={shop} />
        </section>
      </div>
    </ClientLayout>
  );
}
