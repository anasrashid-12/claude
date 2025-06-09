'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop');

  useEffect(() => {
    if (!shop) {
      return;
    }

    // Redirect to backend auth endpoint
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    window.location.href = `${apiUrl}/api/v1/auth/install?shop=${shop}`;
  }, [shop]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-10 shadow">
        <div>
          <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
            Install AI Image Processor
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Please enter your shop domain to continue
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={(e) => {
          e.preventDefault();
          const formData = new FormData(e.currentTarget);
          const shopDomain = formData.get('shop') as string;
          const normalizedShopDomain = shopDomain
            .toLowerCase()
            .trim()
            .replace(/^https?:\/\//, '')
            .replace(/\/$/, '');
          
          router.push(`/login?shop=${normalizedShopDomain}`);
        }}>
          <div className="-space-y-px rounded-md shadow-sm">
            <div>
              <label htmlFor="shop" className="sr-only">
                Shop Domain
              </label>
              <input
                id="shop"
                name="shop"
                type="text"
                required
                className="relative block w-full rounded-md border-0 p-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                placeholder="yourstore.myshopify.com"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
            >
              Install App
            </button>
          </div>
        </form>
      </div>
    </div>
  );
} 