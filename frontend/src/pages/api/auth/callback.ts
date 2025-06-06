import { NextApiRequest, NextApiResponse } from 'next';
import { shopify } from '../../../utils/shopify';
import { SHOPIFY_API_KEY } from '../../../config/shopify';

function getCookieValue(cookies: string | undefined, name: string): string | undefined {
  if (!cookies) return undefined;
  const match = cookies.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? match[2] : undefined;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  try {
    // Get the shop and state from cookies
    const cookies = req.headers.cookie;
    const shopFromCookie = getCookieValue(cookies, 'shopify_shop');
    const stateFromCookie = getCookieValue(cookies, 'shopify_oauth_state');
    
    // Get query parameters
    const { shop, state, code, host } = req.query;

    console.log('Callback received:', {
      shopFromCookie,
      stateFromCookie,
      shopFromQuery: shop,
      stateFromQuery: state,
      hasCode: Boolean(code),
      host
    });

    // Validate the state and shop
    if (!stateFromCookie || state !== stateFromCookie) {
      throw new Error('Invalid OAuth state');
    }

    if (!shopFromCookie || shop !== shopFromCookie) {
      throw new Error('Shop mismatch');
    }

    if (typeof shop !== 'string' || typeof code !== 'string') {
      throw new Error('Invalid shop or code parameter');
    }

    console.log('Starting token exchange...');

    // Exchange the authorization code for an access token
    const accessTokenResponse = await fetch(`https://${shop}/admin/oauth/access_token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        client_id: SHOPIFY_API_KEY,
        client_secret: process.env.SHOPIFY_API_SECRET,
        code,
      }),
    });

    console.log('Token exchange response status:', accessTokenResponse.status);
    
    if (!accessTokenResponse.ok) {
      const errorText = await accessTokenResponse.text();
      console.error('Token exchange error:', errorText);
      throw new Error(`Failed to get access token: ${accessTokenResponse.statusText}. Details: ${errorText}`);
    }

    const tokenData = await accessTokenResponse.json();
    console.log('Token exchange successful:', {
      hasAccessToken: Boolean(tokenData.access_token),
      scope: tokenData.scope,
    });

    // Store the access token securely (implement your storage solution here)
    // For now, we'll just store it in the session
    const session = {
      shop,
      accessToken: tokenData.access_token,
      scope: tokenData.scope,
      isOnline: true,
    };

    // Clear the OAuth cookies
    res.setHeader('Set-Cookie', [
      'shopify_oauth_state=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT',
      'shopify_shop=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT',
    ]);

    // Set cache headers to prevent caching
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');

    // Handle the redirect based on whether it's an embedded app
    if (host) {
      // For embedded apps, redirect to the host
      const embeddedAppUrl = `https://${shop}/admin/apps/${SHOPIFY_API_KEY}?host=${host}`;
      console.log('Redirecting to embedded app URL:', embeddedAppUrl);
      res.redirect(307, embeddedAppUrl);
    } else {
      // For non-embedded apps, redirect to the app home
      const redirectUrl = `/?shop=${shop}`;
      console.log('Redirecting to app home:', redirectUrl);
      res.redirect(307, redirectUrl);
    }
  } catch (error) {
    console.error('OAuth callback error:', error);
    res.status(500).json({
      error: 'Error during OAuth callback',
      details: error instanceof Error ? error.message : 'Unknown error',
    });
  }
} 