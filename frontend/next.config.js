/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
          const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
          return [
            {
                      source: '/api/:path*',
                      destination: `${backendUrl}/api/:path*`,
            },
            {
                      source: '/output/:path*',
                      destination: `${backendUrl}/output/:path*`,
            },
                ];
    },
};

module.exports = nextConfig;
