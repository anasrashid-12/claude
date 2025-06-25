import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

  if (!backendUrl) {
    return NextResponse.json(
      { error: 'Backend URL not configured' },
      { status: 500 }
    );
  }

  try {
    const backendRes = await fetch(`${backendUrl}/me`, {
      method: 'GET',
      headers: {
        Cookie: req.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    const data = await backendRes.json();

    return NextResponse.json(data, {
      status: backendRes.status,
    });
  } catch (error) {
    console.error('[API /me] Error:', error);
    return NextResponse.json(
      { error: 'Session check failed' },
      { status: 500 }
    );
  }
}
