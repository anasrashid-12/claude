'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface ShopifyContextType {
  shop: string | null;
  setShop: (shop: string | null) => void;
}

const ShopifyContext = createContext<ShopifyContextType | undefined>(undefined);

export function useShopify() {
  const context = useContext(ShopifyContext);
  if (context === undefined) {
    throw new Error('useShopify must be used within a ShopifyProvider');
  }
  return context;
}

interface ShopifyProviderProps {
  children: ReactNode;
}

export function ShopifyProvider({ children }: ShopifyProviderProps) {
  const [shop, setShop] = useState<string | null>(null);

  useEffect(() => {
    // Get shop from URL on initial load
    const params = new URLSearchParams(window.location.search);
    const shopParam = params.get('shop');
    if (shopParam) {
      setShop(shopParam);
    }
  }, []);

  const value = {
    shop,
    setShop,
  };

  return (
    <ShopifyContext.Provider value={value}>
      {children}
    </ShopifyContext.Provider>
  );
} 