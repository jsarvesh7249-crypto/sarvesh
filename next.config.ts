import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },

  ...(process.env.GITHUB_ACTIONS === "true" && process.env.GITHUB_REPOSITORY
    ? (() => {
        const repoName = process.env.GITHUB_REPOSITORY.split("/")[1];
        const basePath = `/${repoName}`;
        return {
          basePath,
          assetPrefix: `${basePath}/`,
        };
      })()
    : {}),
};

export default nextConfig;
