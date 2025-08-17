import { useEffect, useState, createContext, useContext, useCallback } from "react";
import { createClient } from "@supabase/supabase-js";
import useShop from "@/hooks/useShop";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

type CreditsContextType = {
  credits: number;
  refreshCredits: () => Promise<void>;
};

const CreditsContext = createContext<CreditsContextType>({
  credits: 0,
  refreshCredits: async () => {},
});

export function CreditsProvider({ children }: { children: React.ReactNode }) {
  const [credits, setCredits] = useState(0);
  const shop = useShop();

  // ✅ Manual refresh
  const refreshCredits = useCallback(async () => {
    if (!shop) return;
    const res = await fetch("/api/credits");
    if (res.ok) {
      const data = await res.json();
      setCredits(data.credits);
    }
  }, [shop]);

  useEffect(() => {
    if (!shop) return;

    // initial fetch
    refreshCredits();

    // realtime subscription
    const channel = supabase
      .channel(`credits-${shop}`)
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "shop_credits",
          filter: `shop_domain=eq.${shop}`,
        },
        (payload) => {
          if (payload.new?.credits !== undefined) {
            setCredits(payload.new.credits);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [shop, refreshCredits]);

  return (
    <CreditsContext.Provider value={{ credits, refreshCredits }}>
      {children}
    </CreditsContext.Provider>
  );
}

export function useCredits() {
  return useContext(CreditsContext);
}
