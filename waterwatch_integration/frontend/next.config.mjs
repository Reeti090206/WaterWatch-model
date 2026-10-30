/** @type {import('next').NextConfig} */
const rawUrl = process.env.BACKEND_API_URL || process.env.FASTAPI_BACKEND_URL || 'http://127.0.0.1:8080';
const backendUrl = rawUrl.replace(/\/+$/, '');

const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
