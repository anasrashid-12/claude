import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const url = request.nextUrl;
  const searchParams = url.searchParams;
  const shop = searchParams.get('shop');
  const host = searchParams.get('host');

  // Skip middleware for API routes
  if (url.pathname.startsWith('/api/')) {
    return NextResponse.next();
  }

  // If we're missing shop or host parameters, redirect to auth
  if (!shop || !host) {
    const authUrl = `/api/auth?shop=${shop || ''}&host=${host || ''}`;
    return NextResponse.redirect(new URL(authUrl, request.url));
  }

  // Add CSP headers for App Bridge
  const response = NextResponse.next();
  
  response.headers.set(
    'Content-Security-Policy',
    [
      `frame-ancestors https://${shop} https://admin.shopify.com;`,
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.shopify.com https://app.shopify.com;",
      "style-src 'self' 'unsafe-inline' https://cdn.shopify.com;",
      "connect-src 'self' https://*.shopify.com https://monorail-edge.shopifysvc.com;",
      "frame-src 'self' https://*.shopify.com https://admin.shopify.com;",
      "img-src 'self' data: blob: https://*.shopify.com https://cdn.shopify.com;",
    ].join(' ')
  );

  // Redirect HTTP to HTTPS
  if (request.headers.get('x-forwarded-proto') === 'http') {
    const httpsUrl = `https://${request.headers.get('host')}${request.nextUrl.pathname}${request.nextUrl.search}`;
    return NextResponse.redirect(httpsUrl, 301);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * 1. /api/ routes
     * 2. /_next/ (Next.js internals)
     * 3. /_static (inside /public)
     * 4. /_vercel (Vercel internals)
     * 5. /favicon.ico, /sitemap.xml (static files)
     */
    '/((?!api/|_next/|_static/|_vercel|favicon.ico|sitemap.xml).*)',
  ],
}; 