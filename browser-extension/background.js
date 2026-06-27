const SHADOWAI_API = "http://localhost:8000/api/proxy/inspect";

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "SHADOWAI_INSPECT") {
    return false;
  }

  fetch(SHADOWAI_API, {
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
