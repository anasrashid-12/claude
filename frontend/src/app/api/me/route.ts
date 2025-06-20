// frontend/app/api/me/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const backendRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/me`, {
      method: 'GET',
      headers: {
        Cookie: req.headers.get('cookie') || '',
      },
    });

    const data = await backendRes.json();

    return new NextResponse(JSON.stringify(data), {
      status: backendRes.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch {
    return new NextResponse(JSON.stringify({ error: 'Session check failed' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
