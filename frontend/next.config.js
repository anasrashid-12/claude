const path = require('path');

const nextConfig = {
  experimental: {
    serverActions: {},
  },

  images: {
    domains: [
      'ftnkfcuhjmmedmoekvwg.supabase.co',
      'vsqljedbhbgufysbdics.supabase.co',
      'avatars.githubusercontent.com',
    ],
  },

  webpack(config) {
    config.resolve.alias['@'] = path.resolve(__dirname, 'src');
    return config;
  },

  async headers() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || '';
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
    let wsSupabase = '';

    try {
      if (supabaseUrl) {
        wsSupabase = `wss://${new URL(supabaseUrl).hostname}`;
      }
    } catch {
      console.warn('Invalid SUPABASE URL in env');
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
                ${backendUrl} 
                ${supabaseUrl} 
                ${wsSupabase} 
                wss://*.supabase.co 
                blob: 
                data:;
              media-src 'self' blob: data:;
              object-src 'none';
            `.replace(/\n/g, '').trim(),
          },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
        ],
      },
    ];
  },
};

const { withSentryConfig } = require('@sentry/nextjs');

module.exports = withSentryConfig(nextConfig, {
  org: 'ai-image',
  project: 'javascript-nextjs',
  silent: !process.env.CI,
  widenClientFileUpload: true,
  disableLogger: true,
  automaticVercelMonitors: true,
});
