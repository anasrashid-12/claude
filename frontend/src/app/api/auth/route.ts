import '@shopify/shopify-api/adapters/node';
import { NextRequest, NextResponse } from 'next/server';
import { shopifyApi, LATEST_API_VERSION } from '@shopify/shopify-api';
import { SHOPIFY_CONFIG, SHOPIFY_APP_URL, SHOPIFY_API_KEY, SCOPES } from '@/config/shopify';
import { generateNonce, generateAuthUrl } from '@/utils/shopify';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  const url = new URL(request.url);
  const shop = url.searchParams.get('shop');
  const error = url.searchParams.get('error');

  // Handle error parameter
  if (error === 'missing_shop') {
    return NextResponse.json(
      { 
        error: 'Missing shop parameter', 
        message: 'Please provide a shop parameter to continue. The shop parameter should be your Shopify store domain (e.g., your-store.myshopify.com).'
      },
      { status: 400 }
    );
  }

  if (!shop) {
    return NextResponse.json(
      { 
        error: 'Missing shop parameter',
        message: 'Please provide a shop parameter to continue. The shop parameter should be your Shopify store domain (e.g., your-store.myshopify.com).'
      },
      { status: 400 }
    );
  }

  // Validate shop format
  if (!shop.match(/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/)) {
    return NextResponse.json(
      { 
        error: 'Invalid shop parameter',
        message: 'The shop parameter must be a valid Shopify store domain (e.g., your-store.myshopify.com).'
      },
      { status: 400 }
    );
  }

  // Construct the authorization URL
  const redirectUri = `${SHOPIFY_APP_URL}/api/auth/callback`;
  const nonce = Math.random().toString(36).substring(2);
  
  const authUrl = `https://${shop}/admin/oauth/authorize?` +
    `client_id=${SHOPIFY_API_KEY}&` +
    `scope=${SCOPES.join(',')}&` +
    `redirect_uri=${encodeURIComponent(redirectUri)}&` +
    `state=${nonce}`;

  // Store nonce in session for validation
  const response = NextResponse.redirect(authUrl);
  response.cookies.set('shopify_nonce', nonce, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax'
  });

  return response;
} 