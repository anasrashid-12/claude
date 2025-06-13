'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const shop = searchParams.get('shop');
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isValidShopDomain = (domain: string) =>
    /^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$/.test(domain);

  useEffect(() => {
    if (!shop) return;

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
      console.error('Missing NEXT_PUBLIC_API_URL in environment variables');
      return;
    }

    if (isValidShopDomain(shop)) {
      setIsRedirecting(true);
      router.push(`${apiUrl}/api/v1/auth/install?shop=${shop}`);
    } else {
      setError('Invalid shop domain.');
      setIsRedirecting(false);
    }
  }, [shop, router]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const shopDomain = formData.get('shop') as string;
    const normalizedShopDomain = shopDomain
      .toLowerCase()
      .trim()
      .replace(/^https?:\/\//, '')
      .replace(/\/$/, '');

    if (!isValidShopDomain(normalizedShopDomain)) {
      setError('Please enter a valid Shopify domain (e.g., mystore.myshopify.com).');
      return;
    }

    setError(null);
    setIsRedirecting(true);
    router.push(`/login?shop=${normalizedShopDomain}`);
  };

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

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
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
                autoFocus
                enterKeyHint="go"
                className="relative block w-full rounded-md border-0 p-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:z-10 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                placeholder="e.g. mystore.myshopify.com"
              />
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-600 font-medium">{error}</p>
          )}

          <div>
            <button
              type="submit"
              disabled={isRedirecting}
              className={`group relative flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white ${
                isRedirecting ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-500'
              } focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600`}
            >
              {isRedirecting ? 'Redirecting...' : 'Install App'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
