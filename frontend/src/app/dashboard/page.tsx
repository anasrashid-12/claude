'use client';

import { useEffect, useState } from 'react';
import UploadSection from '../../../components/UploadSection';
import ImageGallery from '../../../components/ImageGallery';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  const [shop, setShop] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchShop() {
      try {
        const res = await fetch('http://localhost:8000/me', {
          credentials: 'include',
        });
        if (!res.ok) throw new Error('Unauthorized');
        const data = await res.json();
        setShop(data.shop);
      } catch (err) {
        router.push('/');
      } finally {
        setLoading(false);
      }
    }
    fetchShop();
  }, []);

  if (loading) return <p className="p-4">Loading...</p>;
  if (!shop) return null;

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Maxflow Dashboard</h1>
      <UploadSection shop={shop} />
      <ImageGallery shop={shop} />
    </div>
  );
}
