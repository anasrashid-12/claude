import { NextRequest, NextResponse } from 'next/server';

export function middleware(req: NextRequest) {
  const url = req.nextUrl;

  const host = url.searchParams.get('host');
  const shop = url.searchParams.get('shop');
  const session = url.searchParams.get('session');

  const response = NextResponse.next();

  const cookieOptions = {
    secure: true,
    sameSite: 'none' as const,
    path: '/',
    maxAge: 60 * 60 * 24 * 7,
  };

  if (host) {
    response.cookies.set('host', host, cookieOptions);
    console.log('🍪 Set host cookie:', host);
  }

  if (shop) {
    response.cookies.set('shop', shop, cookieOptions);
    console.log('🍪 Set shop cookie:', shop);
  }

  if (session) {
    response.cookies.set('session', session, {
      ...cookieOptions,
      httpOnly: true,
    });
    console.log('🍪 Set session cookie');
  }

  // 👉 SKIP removing query params for debugging
  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
