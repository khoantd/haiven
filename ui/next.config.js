// © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  transpilePackages: [
    "antd",
    "@ant-design",
    "@ant-design/pro-chat",
    "rc-util",
    "rc-pagination",
    "rc-picker",
    "rc-tree",
    "rc-table",
    "rc-input",
    "react-intersection-observer",
  ],
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  images: {
    unoptimized: true,
    domains: [], // Add any external image domains if needed
  },
  assetPrefix: "/boba",
  images: { unoptimized: true }, // necessary for output = 'export'
};

if (process.env.NODE_ENV === "development") {
  // forward API calls to Python backend
  nextConfig.rewrites = () => {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8080/api/:path*",
      },
    ];
  };
} else {
  // build a static site, without server-side features
  // only for production build, otherwise rewrites for dev won't work
  nextConfig.output = "export";
}

module.exports = nextConfig;
