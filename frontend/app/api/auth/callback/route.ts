import { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';
import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const shop = url.searchParams.get('shop');
  const code = url.searchParams.get('code');
  const host = url.searchParams.get('host');

  const supabase = createRouteHandlerClient({ cookies });

  try {
    if (code && !shop) {
      // 🔐 If code is from Supabase login redirect
      await supabase.auth.exchangeCodeForSession(code);
      return NextResponse.redirect(new URL('/dashboard', url));
    }

    if (shop && code && host) {
      // 🛒 Shopify OAuth redirect
      // You can store shop data in Supabase here if needed
      // For now, just redirect to dashboard
      return NextResponse.redirect(new URL(`/dashboard?shop=${shop}`, url));
    }

    // 🔁 If missing params
    return new NextResponse('Invalid auth callback. Missing parameters.', { status: 400 });

  } catch (err) {
    console.error('OAuth callback error:', err);
    return new NextResponse('OAuth Error: Something went wrong.', { status: 500 });
  }
}
