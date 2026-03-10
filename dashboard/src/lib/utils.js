/**
 * Safely extracts the hostname from a URL string.
 * Prevents JS crashes if the URL is malformed or missing.
 */
export const getHostname = (url) => {
  if (!url) return 'system';
  try {
    const parsed = new URL(url);
    return parsed.hostname.replace('www.', '');
  } catch (e) {
    console.warn("Malformed URL detected:", url);
    return 'source-link';
  }
};
