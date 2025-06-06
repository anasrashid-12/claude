import { NextApiRequest, NextApiResponse } from 'next';
import { shopify } from '@/utils/shopify';
import { SHOPIFY_API_KEY, SHOPIFY_APP_URL, SHOPIFY_AUTH_CALLBACK_URL } from '../../../config/shopify';
import crypto from 'crypto';

// Required scopes for the app
const REQUIRED_SCOPES = [
  'read_products',
  'write_products',
  'read_files',
  'write_files',
  'read_orders',
  'write_orders'
].join(',');

// Generate a secure random string for OAuth state
function generateNonce(length: number = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

// Validate the shop parameter
function isValidShopDomain(shop: string): boolean {
  const shopRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/;
  return shopRegex.test(shop);
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    res.status(405).send('Method not allowed');
    return;
  }

  const shopDomain = req.query.shop as string;
  const hostName = req.query.host as string;

  try {
    if (!shopDomain) {
      res.status(400).send('Missing shop parameter');
      return;
    }

    if (!isValidShopDomain(shopDomain)) {
      res.status(400).json({
        error: 'Invalid shop domain',
        required: 'Shop must be a valid myshopify.com domain'
      });
      return;
    }

    // Generate a nonce for OAuth state
    const state = generateNonce();

    // Set secure cookies for OAuth state and shop
    res.setHeader('Set-Cookie', [
      `shopify_oauth_state=${state}; Path=/; HttpOnly; SameSite=Lax`,
      `shopify_shop=${shopDomain}; Path=/; HttpOnly; SameSite=Lax`
    ]);

    // Log auth configuration
    console.log('Auth Configuration:', {
      apiKey: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY ? 'Set' : 'Not Set',
      appUrl: 'http://localhost:3000', // Explicitly use HTTP
      shop: shopDomain,
      host: hostName,
      state: state
    });

    // Generate the auth URL using our custom function
    const authUrl = `https://${shopDomain}/admin/oauth/authorize?` + new URLSearchParams({
      client_id: SHOPIFY_API_KEY,
      scope: REQUIRED_SCOPES,
      redirect_uri: SHOPIFY_AUTH_CALLBACK_URL,
      state: state
    }).toString();

    console.log('Generated auth URL:', authUrl);

    // Use res.redirect() without returning
    res.redirect(authUrl);
  } catch (error: any) {
    console.error('Auth error:', error);
    res.status(500).json({
      error: 'Error initializing OAuth',
      details: error instanceof Error ? error.message : 'Unknown error',
      config: {
        apiKeySet: Boolean(SHOPIFY_API_KEY),
        appUrlSet: Boolean(SHOPIFY_APP_URL),
        shop: shopDomain,
        host: hostName,
      }
    });
  }
} 