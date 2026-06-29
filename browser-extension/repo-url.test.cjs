const assert = require("node:assert/strict");
const { getGitHubRepoUrl } = require("./repo-url");

assert.equal(
  getGitHubRepoUrl("https://github.com/Ankit-builds1/shadowai-guardian"),
  "https://github.com/Ankit-builds1/shadowai-guardian"
);
assert.equal(
  getGitHubRepoUrl("https://github.com/Ankit-builds1/shadowai-guardian/tree/main/browser-extension"),
  "https://github.com/Ankit-builds1/shadowai-guardian"
);
assert.equal(getGitHubRepoUrl("https://github.com/issues"), "");
assert.equal(getGitHubRepoUrl("https://chatgpt.com/"), "");

console.log("repo-url tests passed");
