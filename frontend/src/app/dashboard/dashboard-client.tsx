'use client';

import { useEffect, useState } from 'react';
import useShop from '@/hooks/useShop';
import DashboardHeader from '@/components/DashboardHeader';
import StatsGrid from '@/components/StatsGrid';
import RecentImportsTable from '@/components/RecentImportsTable';
import ComingSoonFeatures from '@/components/ComingSoonFeatures';
import { getSupabase } from '../../../utils/supabase/supabaseClient';

interface ImageEntry {
  image_url: string;
  processed_url: string | null;
  status: string;
  created_at: string;
}

export default function DashboardClient() {
  const { shop, loading: shopLoading } = useShop();
  const [stats, setStats] = useState({
    total: 0,
    processing: 0,
    failed: 0,
    completed: 0,
  });
  const [recent, setRecent] = useState<
    { url: string; product: string; status: string }[]
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!shop) return;
  
    const fetchStats = async () => {
      setLoading(true);
      try {
        const res = await fetch('/api/dashboard-stats', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ shop }),
        });
  
        const { stats, recent, error } = await res.json();
  
        if (error) {
          console.error('❌ API error:', error);
        } else {
          setStats(stats);
          setRecent(recent);
        }
      } catch (err) {
        console.error('❌ Fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
  
    fetchStats();
  }, [shop]);

  if (shopLoading || loading) {
    return (
      <div className="p-6 flex justify-center items-center h-64 text-gray-500 dark:text-gray-300">
        Loading dashboard...
      </div>
    );
  }

  if (!shop) {
    return (
      <div className="p-6 text-red-500 font-medium">
        ❌ Unauthorized. Please open the app from your Shopify Admin.
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-6 pt-10 pb-16 max-w-6xl mx-auto text-gray-900 dark:text-white">
      <DashboardHeader
        title="📊 Dashboard"
        subtitle="Welcome to MaxFlow, your e-commerce automation dashboard."
      />

      <div className="rounded-xl bg-white dark:bg-[#1e293b] p-6 shadow-lg my-6">
        <StatsGrid {...stats} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl bg-white dark:bg-[#1e293b] p-6 shadow-lg">
          <RecentImportsTable items={recent} />
        </div>

        <div className="rounded-xl bg-white dark:bg-[#1e293b] p-6 shadow-lg">
          <ComingSoonFeatures />
        </div>
      </div>
    </div>
  );
}
