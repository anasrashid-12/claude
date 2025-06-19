'use client';

import { useState } from 'react';

export default function HomePage() {
  const [shop, setShop] = useState('');
  const [error, setError] = useState('');

  const handleInstall = () => {
    const input = shop.trim().toLowerCase();
    const shopDomain = input.endsWith('.myshopify.com')
      ? input
      : `${input}.myshopify.com`;

    const isValid = /^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$/.test(shopDomain);
    if (!isValid) {
      setError('⚠️ Enter a valid Shopify domain like "yourstore" or "yourstore.myshopify.com"');
      return;
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backendUrl) {
      setError('Backend URL is not configured');
      return;
    }

    window.location.href = `${backendUrl}/auth/install?shop=${encodeURIComponent(shopDomain)}`;
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Maxflow Image App</h1>
      <p className="text-gray-600 mb-8 text-center max-w-md">
        Connect your Shopify store to begin using AI-powered image enhancements.
      </p>
      <div className="flex flex-col items-center gap-4 w-full max-w-sm">
        <input
          type="text"
          value={shop}
          onChange={(e) => {
            setShop(e.target.value);
            setError('');
          }}
          placeholder="your-store.myshopify.com"
          className="border border-gray-300 p-2 rounded w-full"
        />
        {error && <p className="text-sm text-red-600 text-center">{error}</p>}
        <button
          onClick={handleInstall}
          className="bg-black text-white px-4 py-2 rounded w-full hover:bg-gray-800"
        >
          Install App
        </button>
      </div>
    </main>
  );
}
