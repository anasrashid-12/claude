'use client';

import { useEffect, useState } from 'react';
import useShop from '@/hooks/useShop';
import DashboardHeader from '@/components/DashboardHeader';
import StatsGrid from '@/components/StatsGrid';
import RecentImportsTable from '@/components/RecentImportsTable';
import ComingSoonFeatures from '@/components/ComingSoonFeatures';
import { getSupabase } from '../../../utils/supabaseClient'; 

export default function DashboardClient() {
  const { shop, loading: shopLoading } = useShop();
  const [stats, setStats] = useState({
    total: 0,
    processing: 0,
    failed: 0,
    completed: 0,
  });
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!shop) return;
  
    const supabase = getSupabase();
  
    const fetchStats = async () => {
      setLoading(true);
      try {
        const { data: images, error } = await supabase
          .from('images')
          .select('*')
          .eq('shop', shop)
          .order('created_at', { ascending: false });
  
        if (error) {
          console.error('❌ Supabase error:', error.message);
          return;
        }
  
        setStats({
          total: images.length,
          processing: images.filter((img: any) => ['processing', 'queued'].includes(img.status)).length,
          failed: images.filter((img: any) => ['failed', 'error'].includes(img.status)).length,
          completed: images.filter((img: any) => ['processed', 'completed'].includes(img.status)).length,
        });
  
        setRecent(
          images
            .filter((img: any) => img.processed_url)
            .slice(0, 5)
            .map((img: any) => ({
              url: img.processed_url,
              product: img.image_url?.split('/').pop() ?? 'Unnamed',
              status: img.status,
            }))
        );
      } catch (error) {
        console.error('❌ Error fetching dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };
  
    // Initial fetch
    fetchStats();
  
    // Subscribe to realtime updates for this shop
    const channel = supabase
      .channel('realtime-images-dashboard')
      .on(
        'postgres_changes',
        {
          event: '*', // can be 'INSERT', 'UPDATE', 'DELETE'
          schema: 'public',
          table: 'images',
          filter: `shop=eq.${shop}`,
        },
        (payload) => {
          console.log('🔄 Realtime update:', payload);
          fetchStats(); // refresh dashboard on any change
        }
      )
      .subscribe();
  
    return () => {
      supabase.removeChannel(channel);
    };
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
