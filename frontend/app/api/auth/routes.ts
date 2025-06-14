import { NextResponse } from 'next/server'
export async function GET(req: Request) {
  const shop = new URL(req.url).searchParams.get('shop')
  return NextResponse.redirect(`${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/install?shop=${shop}`)
}
