'use client';

import { useAppBridge } from '@shopify/app-bridge-react';
import { authenticatedFetch } from '@shopify/app-bridge-utils';

export function useAuthenticatedFetch() {
  const app = useAppBridge();
  return authenticatedFetch(app);
}
