export const SHOPIFY_APP_URL = process.env.SHOPIFY_APP_URL || 'https://localhost:3000';
export const SHOPIFY_API_KEY = process.env.SHOPIFY_API_KEY || '';
export const SHOPIFY_API_SECRET = process.env.SHOPIFY_API_SECRET || '';
export const SCOPES = [
  'read_products',
  'write_products',
  'read_files',
  'write_files',
  'read_inventory',
  'write_inventory'
];

export const SHOPIFY_AUTH_CALLBACK_PATH = '/api/auth/callback';
export const SHOPIFY_AUTH_PATH = '/api/auth';

export const SHOPIFY_CONFIG = {
  API_KEY: process.env.SHOPIFY_API_KEY || '',
  API_SECRET_KEY: process.env.SHOPIFY_API_SECRET_KEY || '',
  SCOPES: [
    'read_products',
    'write_products',
    'read_files',
    'write_files',
    'read_orders',
    'write_orders'
  ],
  HOST_NAME: process.env.SHOPIFY_APP_URL || '',
  IS_EMBEDDED_APP: true,
  API_VERSION: '2024-01'
}; 