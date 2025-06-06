const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_SHOPIFY_API_KEY: process.env.NEXT_PUBLIC_SHOPIFY_API_KEY,
    NEXT_PUBLIC_SHOPIFY_APP_URL: process.env.NEXT_PUBLIC_SHOPIFY_APP_URL,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `frame-ancestors https://*.myshopify.com https://admin.shopify.com;`,
          },
        ],
      },
    ];
  },
  images: {
    domains: ['cdn.shopify.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  },
  // Add rewrites for API endpoints
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  transpilePackages: ['@shopify/polaris'],
  // Enable SWC minification
  swcMinify: true,
  // Enable compression
  compress: true,
  // Enable source maps in production for better error tracking
  productionBrowserSourceMaps: true,
  // Increase build performance
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  webpack: (config, { dev, isServer }) => {
    // Optimize images in production
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        minimize: true,
      }
    }
    return config
  },
};

module.exports = withBundleAnalyzer(nextConfig); 