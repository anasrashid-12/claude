import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

interface ShopifyContextType {
  shop: string | null;
  accessToken: string | null;
  isLoading: boolean;
}

const ShopifyContext = createContext<ShopifyContextType>({
  shop: null,
  accessToken: null,
  isLoading: true,
});

export const useShopify = () => useContext(ShopifyContext);

interface ShopifyProviderProps {
  children: ReactNode;
}

export function ShopifyProvider({ children }: ShopifyProviderProps) {
  const [shop, setShop] = useState<string | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeShopify = () => {
      const params = new URLSearchParams(window.location.search);
      const shopParam = params.get('shop');
      
      if (shopParam) {
        setShop(shopParam);
        // Try to get the access token from cookies or session storage
        const storedToken = sessionStorage.getItem('shopify_access_token');
        if (storedToken) {
          setAccessToken(storedToken);
        }
      }
      setIsLoading(false);
    };

    initializeShopify();
  }, []);

  return (
    <ShopifyContext.Provider value={{ shop, accessToken, isLoading }}>
      {children}
    </ShopifyContext.Provider>
  );
} 