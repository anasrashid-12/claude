'use client';

import { useEffect, useState } from 'react';
import { getSupabase } from '../../utils/supabase/supabaseClient';
import type { RealtimePostgresUpdatePayload } from '@supabase/supabase-js';

interface ShopData {
  shop: string;
  credits: number;
}

interface UseShopResult {
  shop: ShopData | null;
  loading: boolean;
  error: string | null;
  setShop: React.Dispatch<React.SetStateAction<ShopData | null>>;
}

export default function useShop(): UseShopResult {
  const [shop, setShop] = useState<ShopData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const supabase = getSupabase();
    const channel = supabase.channel('public:shop_credits');

    const fetchShop = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
          method: 'GET',
          credentials: 'include',
          headers: { Accept: 'application/json' },
        });

        if (!res.ok) throw new Error(`Auth failed: ${res.status}`);

        const data = await res.json();
        if (isMounted && data.shop) {
          setShop({ shop: data.shop, credits: data.credits ?? 0 });

          // Supabase Realtime subscription for credits
          channel
            .on(
              'postgres_changes',
              {
                event: 'UPDATE',
                schema: 'public',
                table: 'shop_credits',
                filter: `shop_domain=eq.${data.shop}`,
              },
              (payload: RealtimePostgresUpdatePayload<ShopData>) => {
                if (!isMounted) return;
                if (payload?.new?.credits !== undefined) {
                  setShop(prev => prev ? { ...prev, credits: payload.new.credits } : prev);
                }
              }
            )
            .subscribe((status, err) => {
              if (status === 'SUBSCRIBED') console.log('✅ Realtime subscription established');
              if (err) console.error('Realtime subscription error:', err);
            });
        }
      } catch (err: any) {
        console.error('[useShop] Error:', err);
        if (isMounted) setError(err.message || 'Authentication error');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchShop();

    return () => {
      isMounted = false;
      supabase.removeChannel(channel);
    };
  }, []);

  return { shop, loading, error, setShop };
}
