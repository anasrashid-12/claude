import { NextRequest, NextResponse } from 'next/server';
import jwt, { JwtPayload } from 'jsonwebtoken';

function getEnvVar(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`❌ Missing environment variable: ${key}`);
  }
  return value;
}

export async function GET(req: NextRequest) {
  const JWT_SECRET = getEnvVar('JWT_SECRET');

  const token = req.cookies.get('session')?.value;

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized: No session token' }, { status: 401 });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as JwtPayload;

    if (typeof decoded !== 'object' || !decoded?.shop) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }

    return NextResponse.json({ shop: decoded.shop, status: 'authenticated' });
  } catch (error) {
    console.error('JWT verification error:', error);
    return NextResponse.json({ error: 'Invalid session token' }, { status: 401 });
  }
}
