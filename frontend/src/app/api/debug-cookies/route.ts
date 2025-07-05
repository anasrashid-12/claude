import { cookies } from 'next/headers';
import { NextResponse } from 'next/server';

export async function GET() {
  const cookieStore = await cookies(); // ✅ use await
  const allCookies = cookieStore.getAll(); // ✅ now getAll works

  const result = Object.fromEntries(
    allCookies.map((c: { name: string; value: string }) => [c.name, c.value])
  );

  return NextResponse.json({ cookies: result });
}
