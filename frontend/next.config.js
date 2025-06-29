const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true, // ✅ Correct syntax
  },
  webpack(config) {
    config.resolve.alias['@'] = path.resolve(__dirname, 'src');
    return config;
  },
  allowedDevOrigins: [
    'https://74d8-2400-adc1-47c-4e00-61cb-8ef2-722e-c68f.ngrok-free.app',
  ],
};

module.exports = nextConfig;
