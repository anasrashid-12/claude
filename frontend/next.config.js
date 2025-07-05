const path = require('path');
require('dotenv').config();

const nextConfig = {
  experimental: {
    serverActions: {},
  },

  webpack(config) {
    config.resolve.alias['@'] = path.resolve(__dirname, 'src');
    return config;
  },

  async headers() {
    let wsSupabase = '';
    try {
      if (process.env.NEXT_PUBLIC_SUPABASE_URL) {
        wsSupabase = `wss://${new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).hostname}`;
      }
    } catch (e) {
      console.warn('Invalid SUPABASE URL in .env:', e);
    }

    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `
              frame-ancestors https://admin.shopify.com https://*.myshopify.com;
              default-src 'self' https: data: blob:;
              script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
              style-src 'self' 'unsafe-inline' https:;
              img-src 'self' data: blob: https:;
              font-src 'self' https: data:;
              connect-src 
                https://*.shopify.com 
                https://cdn.shopify.com 
                ${process.env.NEXT_PUBLIC_BACKEND_URL}
                ${process.env.NEXT_PUBLIC_SUPABASE_URL}
                ${wsSupabase}
                wss://*.supabase.co 
                blob: 
                data:;
              media-src 'self' blob: data:;
              object-src 'none';
            `.replace(/\n/g, '').trim(),
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
