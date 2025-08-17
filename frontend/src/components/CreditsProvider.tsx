'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { createClient } from '@supabase/supabase-js';

type CreditsContextType = {
  credits: number | null;
  refreshCredits: () => Promise<void>;
};

const CreditsContext = createContext<CreditsContextType | undefined>(undefined);

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export function CreditsProvider({ children }: { children: ReactNode }) {
  const [credits, setCredits] = useState<number | null>(null);

  const refreshCredits = useCallback(async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/credits/me`, {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch credits');
      const data = await res.json();
      setCredits(data.credits);
    } catch (err) {
      console.error('Credit fetch failed:', err);
    }
  }, []);

  useEffect(() => {
    refreshCredits();

    // subscribe to shop_credits table realtime
    const channel = supabase
      .channel('shop-credits-listener')
      .on(
        'postgres_changes',
        {
          event: '*', // INSERT | UPDATE | DELETE
          schema: 'public',
          table: 'shop_credits',
        },
        (payload) => {
          console.log('🔔 Realtime credits update:', payload);
          // backend /credits/me ko call karke fresh credits le aao
          refreshCredits();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [refreshCredits]);

  return (
    <CreditsContext.Provider value={{ credits, refreshCredits }}>
      {children}
    </CreditsContext.Provider>
  );
}

export function useCredits() {
  const ctx = useContext(CreditsContext);
  if (!ctx) throw new Error('useCredits must be used inside <CreditsProvider>');
  return ctx;
}
