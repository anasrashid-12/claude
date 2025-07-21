const path = require('path');
require('dotenv').config();

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
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
        ],
      },
    ];
  },
};

module.exports = nextConfig;


// Injected content via Sentry wizard below

const { withSentryConfig } = require("@sentry/nextjs");

module.exports = withSentryConfig(
  module.exports,
  {
    // For all available options, see:
    // https://www.npmjs.com/package/@sentry/webpack-plugin#options

    org: "ai-image",
    project: "javascript-nextjs",

    // Only print logs for uploading source maps in CI
    silent: !process.env.CI,

    // For all available options, see:
    // https://docs.sentry.io/platforms/javascript/guides/nextjs/manual-setup/

    // Upload a larger set of source maps for prettier stack traces (increases build time)
    widenClientFileUpload: true,

    // Uncomment to route browser requests to Sentry through a Next.js rewrite to circumvent ad-blockers.
    // This can increase your server load as well as your hosting bill.
    // Note: Check that the configured route will not match with your Next.js middleware, otherwise reporting of client-
    // side errors will fail.
    // tunnelRoute: "/monitoring",

    // Automatically tree-shake Sentry logger statements to reduce bundle size
    disableLogger: true,

    // Enables automatic instrumentation of Vercel Cron Monitors. (Does not yet work with App Router route handlers.)
    // See the following for more information:
    // https://docs.sentry.io/product/crons/
    // https://vercel.com/docs/cron-jobs
    automaticVercelMonitors: true,
  }
);
