import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET!;
if (!JWT_SECRET) throw new Error('❌ Missing JWT_SECRET in environment variables.');

export async function GET(req: Request) {
  const authHeader = req.headers.get('Authorization');

  if (!authHeader?.startsWith('Bearer ')) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = authHeader.replace('Bearer ', '');

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as { shop: string };

    if (!decoded?.shop) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }

    return NextResponse.json({ shop: decoded.shop, status: 'authenticated' });
  } catch (error) {
    console.error('JWT verification error:', error);
    return NextResponse.json({ error: 'Invalid session token' }, { status: 401 });
  }
}