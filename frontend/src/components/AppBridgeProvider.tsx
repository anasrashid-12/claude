'use client';

import { ReactNode, useMemo, Suspense } from 'react';
import { Provider } from '@shopify/app-bridge-react';
import { useSearchParams } from 'next/navigation';

interface AppBridgeProviderProps {
  children: ReactNode;
}

function AppBridgeProviderInner({ children }: AppBridgeProviderProps) {
  const searchParams = useSearchParams();
  const host = searchParams.get('host');

  if (!host) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-red-500">❌ Host not found in URL</p>
      </div>
    );
  }

  const config = useMemo(
    () => ({
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!,
      host,
      forceRedirect: true,
    }),
    [host]
  );

  return <Provider config={config}>{children}</Provider>;
}

export default function AppBridgeProvider(props: AppBridgeProviderProps) {
  return (
    <Suspense fallback={<div className="p-4">Loading App...</div>}>
      <AppBridgeProviderInner {...props} />
    </Suspense>
  );
}
