'use client';

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

type CreditsContextType = {
  credits: number | null;
  refreshCredits: () => Promise<void>;
};

const CreditsContext = createContext<CreditsContextType | undefined>(undefined);

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
