// Environment variables
export const SHOPIFY_API_KEY = process.env.NEXT_PUBLIC_SHOPIFY_API_KEY!;
export const SHOPIFY_API_SECRET = process.env.SHOPIFY_API_SECRET!;
export const SHOPIFY_APP_URL = process.env.NEXT_PUBLIC_HOST_URL || 
  (process.env.NODE_ENV === 'development' ? 
    process.env.NEXT_PUBLIC_NGROK_URL || 'http://localhost:3000' : 
    'https://your-production-url.com');
export const SHOPIFY_AUTH_CALLBACK_URL = `${SHOPIFY_APP_URL}/api/auth/callback`;

// Scopes the app needs
export const SCOPES = [
  'read_products',
  'write_products',
  'read_files',
  'write_files',
  'read_orders',
  'write_orders'
] as const;

// API version to use
export const API_VERSION = '2024-01' as const;

// Auth path
export const SHOPIFY_AUTH_PATH = '/api/auth';

// Shopify app configuration
export const SHOPIFY_CONFIG = {
  API_KEY: SHOPIFY_API_KEY,
  API_SECRET_KEY: SHOPIFY_API_SECRET,
  SCOPES,
  HOST_NAME: SHOPIFY_APP_URL.replace(/https?:\/\//, ''),
  IS_EMBEDDED_APP: true,
  API_VERSION
}; 