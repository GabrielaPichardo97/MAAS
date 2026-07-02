import type { EpisodeManifest } from "./types";

export function rebaseAssetUrl(url: string, baseUrl: string): string {
  if (/^(?:[a-z]+:)?\/\//i.test(url) || url.startsWith("data:") || url.startsWith("blob:")) return url;
  const base = `/${baseUrl.replace(/^\/+|\/+$/g, "")}/`.replace("//", "/");
  if (url.startsWith(base)) return url;
  return `${base}${url.replace(/^\/+/, "")}`;
}

export function rebaseManifestAssets(manifest: EpisodeManifest, baseUrl: string): EpisodeManifest {
  return {
    ...manifest,
    assetUrls: Object.fromEntries(
      Object.entries(manifest.assetUrls).map(([assetId, url]) => [assetId, rebaseAssetUrl(url, baseUrl)]),
    ),
  };
}
