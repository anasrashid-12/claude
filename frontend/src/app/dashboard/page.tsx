'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useShop from '../../hooks/useShop';
import UploadSection from '../../../components/UploadSection';
import ImageGallery from '../../../components/ImageGallery';

export default function DashboardPage() {
  const router = useRouter();
  const { shop, loading } = useShop();

  useEffect(() => {
    if (!loading && !shop) {
      router.push('/');
    }
  }, [shop, loading, router]);

  if (loading) {
    return <p className="p-4 text-gray-500">Loading...</p>;
  }

  if (!shop) return null;

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Maxflow Dashboard</h1>
      <UploadSection shop={shop} />
      <ImageGallery shop={shop} />
    </div>
  );
}
