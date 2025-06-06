import { ReactNode, useMemo } from 'react';
import { createApp } from '@shopify/app-bridge';
import { AppBridgeProvider as Provider } from '@shopify/app-bridge-react';

interface AppBridgeProviderProps {
  children: ReactNode;
  config: {
    apiKey: string;
    host: string;
    forceRedirect: boolean;
  };
}

export function AppBridgeProvider({ children, config }: AppBridgeProviderProps) {
  const app = useMemo(() => createApp(config), [config]);

  return <Provider config={config}>{children}</Provider>;
} 