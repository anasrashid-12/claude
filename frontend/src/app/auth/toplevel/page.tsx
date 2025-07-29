'use client';

import { useEffect } from 'react';
import { Redirect } from '@shopify/app-bridge/actions';
import { useAppBridge } from '@shopify/app-bridge-react';
import { useSearchParams } from 'next/navigation';

export default function TopLevelRedirectPage() {
  const app = useAppBridge();
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop');
  const host = searchParams.get('host');

  useEffect(() => {
    const redirectUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/oauth?shop=${shop}&host=${host}`;

    if (window.top === window.self) {
      // Not in an iframe – safe to use form redirect
      const form = document.createElement('form');
      form.method = 'GET';
      form.action = redirectUrl;

      const shopInput = document.createElement('input');
      shopInput.type = 'hidden';
      shopInput.name = 'shop';
      shopInput.value = shop || '';
      form.appendChild(shopInput);

      const hostInput = document.createElement('input');
      hostInput.type = 'hidden';
      hostInput.name = 'host';
      hostInput.value = host || '';
      form.appendChild(hostInput);

      document.body.appendChild(form);
      form.submit();
    } else if (app && shop && host) {
      const redirect = Redirect.create(app);
      redirect.dispatch(Redirect.Action.REMOTE, redirectUrl);
    }
  }, [app, shop, host]);

  return <div className="p-4">🚀 Redirecting to Shopify securely...</div>;
}
