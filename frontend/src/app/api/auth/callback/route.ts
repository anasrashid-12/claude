import '@shopify/shopify-api/adapters/node';
import { NextRequest, NextResponse } from 'next/server';
import { shopifyApi, LATEST_API_VERSION } from '@shopify/shopify-api';
import { SHOPIFY_CONFIG, SHOPIFY_APP_URL } from '@/config/shopify';
import { cookies } from 'next/headers';
import { verifyHmac, getAccessToken } from '@/utils/shopify';
import { SHOPIFY_API_KEY, SHOPIFY_API_SECRET } from '@/config/shopify';

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    const shop = url.searchParams.get('shop');
    const code = url.searchParams.get('code');
    const state = url.searchParams.get('state');
    const hmac = url.searchParams.get('hmac');

    // Validate the request
    if (!shop || !code || !state || !hmac) {
      console.error('Missing required parameters:', { shop, code, state, hmac });
      return NextResponse.json(
        { 
          error: 'Authentication failed',
          message: 'Missing required parameters for authentication'
        },
        { status: 400 }
      );
    }

    // Validate shop format
    if (!shop.match(/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/)) {
      console.error('Invalid shop format:', shop);
      return NextResponse.json(
        { 
          error: 'Authentication failed',
          message: 'Invalid shop format'
        },
        { status: 400 }
      );
    }

    // Validate nonce
    const cookieStore = cookies();
    const storedNonce = cookieStore.get('shopify_nonce');
    if (!storedNonce || storedNonce.value !== state) {
      console.error('Invalid nonce:', { stored: storedNonce?.value, received: state });
      return NextResponse.json(
        { 
          error: 'Authentication failed',
          message: 'Invalid state parameter'
        },
        { status: 403 }
      );
    }

    // Verify HMAC
    if (!verifyHmac(new URLSearchParams(url.search), SHOPIFY_API_SECRET)) {
      console.error('HMAC verification failed');
      return NextResponse.json(
        { 
          error: 'Authentication failed',
          message: 'Invalid request signature'
        },
        { status: 403 }
      );
    }

    // Exchange the authorization code for an access token
    const accessTokenResponse = await fetch(`https://${shop}/admin/oauth/access_token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_id: SHOPIFY_API_KEY,
        client_secret: SHOPIFY_API_SECRET,
        code
      })
    });

    if (!accessTokenResponse.ok) {
      const errorData = await accessTokenResponse.text();
      console.error('Access token request failed:', {
        status: accessTokenResponse.status,
        statusText: accessTokenResponse.statusText,
        error: errorData
      });
      throw new Error('Failed to get access token');
    }

    const { access_token } = await accessTokenResponse.json();
    if (!access_token) {
      console.error('No access token in response');
      throw new Error('No access token received');
    }

    // Create session
    const response = NextResponse.redirect(`${SHOPIFY_APP_URL}?shop=${shop}`);
    
    // Set the session cookie with appropriate security settings
    response.cookies.set('shopify_session', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    });

    // Store shop domain in a separate cookie
    response.cookies.set('shopify_shop_domain', shop, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    });

    // Clear the nonce cookie
    response.cookies.delete('shopify_nonce');

    return response;
  } catch (error) {
    console.error('Auth callback error:', error);
    return NextResponse.json(
      { 
        error: 'Authentication failed',
        message: error instanceof Error ? error.message : 'An unexpected error occurred during authentication'
      },
      { status: 500 }
    );
  }
} 