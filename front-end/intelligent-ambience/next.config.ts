import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  rewrites: async () => {
    return [
      {
        source: "/api/generate",
        destination: "http://127.0.0.1:8000/generate",
      },
    ];
  },
};

export default nextConfig;
