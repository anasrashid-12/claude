import { ReactNode, useEffect, useMemo } from 'react';
import { createApp } from '@shopify/app-bridge';
import { useRouter } from 'next/navigation';

interface AppBridgeProviderProps {
  children: ReactNode;
  config: {
    apiKey: string;
    host: string;
    forceRedirect: boolean;
  };
}

export function AppBridgeProvider({ children, config }: AppBridgeProviderProps) {
  const router = useRouter();

  const app = useMemo(() => {
    return createApp(config);
  }, [config]);

  useEffect(() => {
    // Check if we need to redirect to HTTPS
    if (typeof window !== 'undefined' && window.location.protocol === 'http:') {
      const httpsUrl = `https://${window.location.host}${window.location.pathname}${window.location.search}`;
      window.location.replace(httpsUrl);
      return;
    }
  }, []);

  return <>{children}</>;
} 