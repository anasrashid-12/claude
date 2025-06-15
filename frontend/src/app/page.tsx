'use client';

import { useState } from 'react';

export default function HomePage() {
  const [shop, setShop] = useState('');

  const handleInstall = () => {
    if (!shop) return;
    const shopDomain = shop.replace(/^https?:\/\//, '').replace(/\/$/, '');
    window.location.href = `http://localhost:8000/auth/install?shop=${shopDomain}`;
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-4">Maxflow Image App</h1>
      <p className="text-gray-600 mb-8 text-center max-w-md">
        Connect your Shopify store to get started with AI-powered image processing.
      </p>
      <div className="flex items-center gap-4">
        <input
          type="text"
          value={shop}
          onChange={(e) => setShop(e.target.value)}
          placeholder="your-store.myshopify.com"
          className="border p-2 rounded w-72"
        />
        <button
          onClick={handleInstall}
          className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          Install App
        </button>
      </div>
    </main>
  );
}
