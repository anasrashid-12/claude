import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const shop = req.cookies.get('shopify_shop_domain')?.value;
    const accessToken = req.cookies.get('shopify_access_token')?.value;

    // Verify the access token is valid by making a test request to Shopify
    if (shop && accessToken) {
      const response = await fetch(`https://${shop}/admin/api/2024-01/shop.json`, {
        headers: {
          'X-Shopify-Access-Token': accessToken
        }
      });

      if (response.ok) {
        return NextResponse.json({
          isAuthenticated: true,
          shop,
          accessToken
        });
      }
    }

    return NextResponse.json({
      isAuthenticated: false,
      shop: null,
      accessToken: null
    });
  } catch (error) {
    console.error('Auth verification error:', error);
    return NextResponse.json({
      isAuthenticated: false,
      shop: null,
      accessToken: null
    });
  }
} 