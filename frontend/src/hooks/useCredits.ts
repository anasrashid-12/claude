'use client';

import { useEffect, useState, useCallback } from 'react';

export default function useCredits() {
  const [credits, setCredits] = useState<number | null>(null);

  const refreshCredits = useCallback(async () => {
    try {
      const res = await fetch("/api/credits/me", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch credits");
      const data = await res.json();
      setCredits(data.credits);
    } catch (err) {
      console.error("Credit fetch failed:", err);
    }
  }, []);

  useEffect(() => {
    refreshCredits();
  }, [refreshCredits]);

  return { credits, refreshCredits };
}
