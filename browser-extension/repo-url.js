function getGitHubRepoUrl(pageUrl) {
  try {
    const url = new URL(pageUrl);
    if (url.hostname !== "github.com") return "";
    const parts = url.pathname.split("/").filter(Boolean);
    if (parts.length < 2) return "";
    if (["settings", "notifications", "pulls", "issues", "marketplace", "explore"].includes(parts[0])) return "";
    return `https://github.com/${parts[0]}/${parts[1]}`;
  } catch (_error) {
    return "";
  }
}

if (typeof module !== "undefined") {
  module.exports = { getGitHubRepoUrl };
}
