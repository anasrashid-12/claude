'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { getCookie } from 'cookies-next';
import createApp from '@shopify/app-bridge';
import { Redirect } from '@shopify/app-bridge/actions';

export default function LoginPage() {
  const [shop, setShop] = useState('');
  const [host, setHost] = useState<string | null>(null);
  const searchParams = useSearchParams();

  useEffect(() => {
    const urlHost = searchParams.get('host');
    const cookieHost = getCookie('host') as string | undefined;
    if (urlHost) setHost(urlHost);
    else if (cookieHost) setHost(cookieHost);
  }, [searchParams]);

  const handleLogin = () => {
    let formattedShop = shop.trim();
    if (!formattedShop.endsWith('.myshopify.com')) {
      formattedShop = `${formattedShop}.myshopify.com`;
    }

    if (!/^[a-zA-Z0-9-]+\.myshopify\.com$/.test(formattedShop)) {
      alert('❌ Please enter a valid Shopify domain');
      return;
    }

    if (!host) {
      alert('❌ Missing host parameter. Please open the app from Shopify Admin.');
      return;
    }

    const app = createApp({
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!,
      host,
      forceRedirect: true,
    });

    const redirect = Redirect.create(app);
    redirect.dispatch(Redirect.Action.REMOTE, {
      url: `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/install?shop=${formattedShop}&host=${host}`,
    });
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="p-6 rounded-2xl shadow-xl bg-white dark:bg-gray-800 w-full max-w-sm space-y-4 text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">🧠 Maxflow Image App</h1>

        <input
          type="text"
          placeholder="your-store.myshopify.com"
          value={shop}
          onChange={(e) => setShop(e.target.value)}
          className="border border-gray-300 dark:border-gray-700 px-4 py-2 rounded-md w-full text-sm dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-black"
        />

        <button
          onClick={handleLogin}
          className="w-full bg-black hover:bg-gray-800 text-white rounded-md py-2 text-sm font-semibold transition"
        >
          Install App
        </button>
      </div>
    </div>
  );
}
