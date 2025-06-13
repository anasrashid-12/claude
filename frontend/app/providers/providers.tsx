'use client';

import { AppBridgeProvider } from './app-bridge-provider';
import { QueryClientProviderWrapper } from './react-query-provider';
import { PolarisProvider } from './polaris-provider';

import { createPagesBrowserClient } from '@supabase/auth-helpers-nextjs';
import { SessionContextProvider } from '@supabase/auth-helpers-react';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [supabaseClient] = useState(() => createPagesBrowserClient());

  return (
    <SessionContextProvider supabaseClient={supabaseClient}>
      <AppBridgeProvider>
        <QueryClientProviderWrapper>
          <PolarisProvider>
            {children}
          </PolarisProvider>
        </QueryClientProviderWrapper>
      </AppBridgeProvider>
    </SessionContextProvider>
  );
}
