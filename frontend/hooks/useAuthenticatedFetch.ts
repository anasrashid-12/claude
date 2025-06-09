import { useCallback } from 'react';
import { useAppBridge } from '@shopify/app-bridge-react';
import { authenticatedFetch } from '@shopify/app-bridge-utils';

export function useAuthenticatedFetch() {
  const app = useAppBridge();

  return useCallback(
    async (uri: string, options?: RequestInit) => {
      const fetch = authenticatedFetch(app);
      const response = await fetch(uri, options);

      if (response.headers.get('X-Shopify-API-Request-Failure-Reauthorize') === '1') {
        const authUrlHeader = response.headers.get('X-Shopify-API-Request-Failure-Reauthorize-Url');
        
        if (authUrlHeader) {
          window.location.assign(authUrlHeader);
          return null;
        }
      }

      return response;
    },
    [app]
  );
} 