/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_GRAPHQL_URL:
      process.env.NEXT_PUBLIC_GRAPHQL_URL || "http://localhost:8000/graphql",
  },
};

module.exports = nextConfig;
