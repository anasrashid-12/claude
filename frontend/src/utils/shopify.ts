import { shopifyApi, LATEST_API_VERSION } from '@shopify/shopify-api';
import '@shopify/shopify-api/adapters/node';
import { NextRequest } from 'next/server';
import crypto from 'crypto';
import { SHOPIFY_API_KEY, SHOPIFY_API_SECRET, SCOPES, SHOPIFY_APP_URL } from '@/config/shopify';

const isDevelopment = process.env.NODE_ENV === 'development';

// Initialize the Shopify API client
export const shopify = shopifyApi({
  apiKey: SHOPIFY_API_KEY,
  apiSecretKey: SHOPIFY_API_SECRET,
  scopes: SCOPES,
  hostName: SHOPIFY_APP_URL.replace(/https?:\/\//, ''),
  hostScheme: SHOPIFY_APP_URL.split('://')[0] as 'http' | 'https',
  apiVersion: LATEST_API_VERSION,
  isEmbeddedApp: true,
  isCustomStoreApp: false,
  logger: { level: isDevelopment ? 0 : 4 },
});

// Helper function to convert NextRequest to format Shopify API expects
export function convertNextRequestToShopify(req: NextRequest) {
  const headers = new Headers(req.headers);
  const url = new URL(req.url);

  return {
    headers: headers,
    method: req.method,
    url: url.toString(),
    baseUrl: url.origin,
    path: url.pathname + url.search,
    query: Object.fromEntries(url.searchParams),
    body: null,
    rawBody: null,
    status: 200,
    statusText: 'OK',
    statusCode: 200,
    statusMessage: 'OK',
    get: (name: string) => headers.get(name),
    set: (name: string, value: string) => headers.set(name, value),
    has: (name: string) => headers.has(name),
    delete: (name: string) => headers.delete(name),
    append: (name: string, value: string) => headers.append(name, value),
    getAll: () => Array.from(headers.entries()),
    raw: () => headers
  };
}

export function generateNonce(length = 32): string {
  return crypto.randomBytes(length).toString('hex');
}

export function verifyHmac(query: URLSearchParams, secret: string): boolean {
  try {
    const hmac = query.get('hmac');
    if (!hmac) return false;

    // Create a new URLSearchParams without the hmac
    const params = new URLSearchParams(query);
    params.delete('hmac');

    // Sort the parameters
    const sortedParams = new URLSearchParams();
    Array.from(params.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .forEach(([key, value]) => sortedParams.append(key, value));

    const message = sortedParams.toString();
    const generatedHash = crypto
      .createHmac('sha256', secret)
      .update(message)
      .digest('hex');

    return crypto.timingSafeEqual(
      Buffer.from(hmac),
      Buffer.from(generatedHash)
    );
  } catch (error) {
    console.error('HMAC verification error:', error);
    return false;
  }
}

export function generateAuthUrl(shop: string, nonce: string): string {
  if (!shop || !nonce) {
    throw new Error('Shop and nonce are required for generating auth URL');
  }

  if (!shop.match(/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/)) {
    throw new Error('Invalid shop domain format');
  }

  const baseUrl = `https://${shop}/admin/oauth/authorize`;
  const params = new URLSearchParams({
    client_id: SHOPIFY_API_KEY,
    scope: SCOPES.join(','),
    redirect_uri: `${SHOPIFY_APP_URL}/api/auth/callback`,
    state: nonce,
  });

  return `${baseUrl}?${params.toString()}`;
}

export async function getAccessToken(shop: string, code: string): Promise<{ access_token: string }> {
  if (!shop || !code) {
    throw new Error('Shop and code are required for getting access token');
  }

  const response = await fetch(`https://${shop}/admin/oauth/access_token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      client_id: SHOPIFY_API_KEY,
      client_secret: SHOPIFY_API_SECRET,
      code,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get access token: ${error}`);
  }

  const data = await response.json();
  if (!data.access_token) {
    throw new Error('No access token received from Shopify');
  }

  return data;
}

export function getShopifyClient(accessToken: string, shop: string) {
  if (!accessToken || !shop) {
    throw new Error('Access token and shop are required for Shopify client');
  }

  return {
    async graphql<T = any>(query: string, variables = {}) {
      const response = await fetch(`https://${shop}/admin/api/2024-01/graphql.json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Shopify-Access-Token': accessToken,
        },
        body: JSON.stringify({
          query,
          variables,
        }),
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`GraphQL request failed: ${error}`);
      }

      const data = await response.json();
      if (data.errors) {
        throw new Error(
          `GraphQL errors: ${JSON.stringify(data.errors)}`
        );
      }

      return data as T;
    },
  };
} 