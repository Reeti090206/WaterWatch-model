/** @type {import('next').NextConfig} */

function getBackendUrl() {
  let url = (
    process.env.BACKEND_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.FASTAPI_BACKEND_URL ||
    'https://waterwatch-backend-hv27.onrender.com'
  ).trim();

  if (!url) {
    url = 'https://waterwatch-backend-hv27.onrender.com';
  }

  // Strip wrapping quotes
  url = url.replace(/^["']+|["']+$/g, '');

  // Strip trailing /api/v1 if included
  url = url.replace(/\/api\/v1\/?$/, '');

  // Strip trailing slashes
  url = url.replace(/\/+$/, '');

  // Ensure valid HTTP/HTTPS protocol
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = `https://${url}`;
  }

  return url;
}

const backendUrl = getBackendUrl();

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
