const SHADOWAI_PROMPT_API = "http://localhost:8000/api/proxy/inspect";
const SHADOWAI_REPO_API = "http://localhost:8000/api/scan/github";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!["SHADOWAI_INSPECT", "SHADOWAI_SCAN_REPO"].includes(message?.type)) {
    return false;
  }

  const endpoint = message.type === "SHADOWAI_SCAN_REPO" ? SHADOWAI_REPO_API : SHADOWAI_PROMPT_API;

  fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(message.payload)
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`Local proxy returned ${response.status}`);
      }
      sendResponse({ ok: true, data: await response.json() });
    })
    .catch((error) => {
      sendResponse({ ok: false, error: error.message });
    });

  return true;
});
