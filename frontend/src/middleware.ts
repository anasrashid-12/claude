import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { SHOPIFY_AUTH_PATH } from './config/shopify';

export async function middleware(request: NextRequest) {
  const shop = request.nextUrl.searchParams.get('shop');
  const session = request.cookies.get('shopify_session');
  const isEmbedded = request.headers.get('sec-fetch-dest') === 'iframe';

  // Skip auth for API routes and auth paths
  if (
    request.nextUrl.pathname.startsWith('/api/') ||
    request.nextUrl.pathname.startsWith(SHOPIFY_AUTH_PATH)
  ) {
    return NextResponse.next();
  }

  // If we're not embedded and there's no shop parameter,
  // show a friendly error page instead of redirecting
  if (!shop && !isEmbedded && !request.nextUrl.pathname.startsWith(SHOPIFY_AUTH_PATH)) {
    return NextResponse.rewrite(new URL('/install', request.url));
  }

  // If we're embedded but have no session, redirect to auth
  if (!session) {
    const authUrl = shop 
      ? `${SHOPIFY_AUTH_PATH}?shop=${shop}`
      : SHOPIFY_AUTH_PATH;
    return NextResponse.redirect(new URL(authUrl, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all paths except for:
     * 1. /api routes
     * 2. /_next (Next.js internals)
     * 3. /_static (inside /public)
     * 4. all root files inside /public (e.g. /favicon.ico)
     */
    '/((?!api/|_next/|_static/|_vercel|[\\w-]+\\.\\w+).*)',
  ],
}; 