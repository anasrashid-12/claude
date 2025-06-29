'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [shop, setShop] = useState('');
  const router = useRouter();

  const handleLogin = () => {
    let formattedShop = shop.trim();

    if (!formattedShop.endsWith('.myshopify.com')) {
      formattedShop = `${formattedShop}.myshopify.com`;
    }

    const valid = /^[a-zA-Z0-9-]+\.myshopify\.com$/.test(formattedShop);
    if (!valid) {
      alert('❌ Invalid Shopify domain');
      return;
    }

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backendUrl) {
      alert('❌ Backend URL not configured');
      return;
    }

    router.push(`${backendUrl}/auth/install?shop=${formattedShop}`);
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <div className="p-6 rounded-2xl shadow-xl bg-white w-[400px]">
        <h1 className="text-2xl font-bold mb-4 text-center">Maxflow Image App</h1>
        <input
          type="text"
          placeholder="Enter your shop domain"
          className="border border-gray-300 px-4 py-2 rounded-md w-full mb-4 focus:outline-none focus:ring-2 focus:ring-black"
          value={shop}
          onChange={(e) => setShop(e.target.value)}
        />
        <button
          className="w-full bg-black text-white rounded-md py-2 hover:bg-gray-800 transition"
          onClick={handleLogin}
        >
          Install App
        </button>
      </div>
    </div>
  );
}
