'use client';

import { useSearchParams } from 'next/navigation';
import UploadSection from '../../../components/UploadSection'; 
import ImageGallery from '../../../components/ImageGallery';

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop') || 'ai-image-app-dev-store.myshopify.com';

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Maxflow Dashboard</h1>
      <UploadSection shop={shop} />
      <ImageGallery shop={shop} />
    </div>
  );
}
