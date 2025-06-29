import { NextRequest, NextResponse } from 'next/server';

export function middleware(req: NextRequest) {
  const url = req.nextUrl;

  const host = url.searchParams.get('host');
  const session = url.searchParams.get('session');
  const shop = url.searchParams.get('shop');

  const response = NextResponse.next();

  if (host) {
    response.cookies.set('host', host, {
      httpOnly: true,
      secure: true,
      sameSite: 'none',
      path: '/',
    });
  }

  if (session) {
    response.cookies.set('session', session, {
      httpOnly: true,
      secure: true,
      sameSite: 'none',
      path: '/',
    });
  }

  if (shop) {
    response.cookies.set('shop', shop, {
      httpOnly: true,
      secure: true,
      sameSite: 'none',
      path: '/',
    });
  }

  // Remove these params from URL after setting cookies
  if (host || session || shop) {
    url.searchParams.delete('host');
    url.searchParams.delete('session');
    url.searchParams.delete('shop');

    return NextResponse.redirect(url, {
      status: 302,
      headers: response.headers,
    });
  }

  return response;
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
