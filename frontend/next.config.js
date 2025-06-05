const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_SHOPIFY_API_KEY: process.env.SHOPIFY_API_KEY,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: 'frame-ancestors https://*.myshopify.com https://*.shopify.com https://admin.shopify.com https://shop.app;',
          },
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-Requested-With, Content-Type, Authorization, Accept',
          },
          {
            key: 'X-Frame-Options',
            value: 'ALLOWALL'
          }
        ],
      },
    ];
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
  // Enable React strict mode for better development
  reactStrictMode: true,
  // Allow Shopify domains in images
  images: {
    domains: ['cdn.shopify.com', 'shop.app', 'admin.shopify.com'],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
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