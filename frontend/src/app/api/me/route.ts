// frontend/app/api/me/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
    credentials: 'include',
    headers: {
      Cookie: req.headers.get('cookie') || '',
    },
  });

  const data = await res.json();
  return new NextResponse(JSON.stringify(data), { status: res.status });
}
