import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useShopify } from '../providers/ShopifyProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, shop } = useShopify();

  useEffect(() => {
    if (!isAuthenticated) {
      const authUrl = new URL('/api/auth', window.location.origin);
      if (shop) {
        authUrl.searchParams.set('shop', shop);
      }
      router.push(authUrl.toString());
    }
  }, [isAuthenticated, router, shop]);

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Authenticating...</h2>
          <p className="text-gray-600">Please wait while we connect to your Shopify store.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
} 