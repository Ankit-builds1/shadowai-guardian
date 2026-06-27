const SHADOWAI_API = "http://localhost:8000/api/proxy/inspect";
const DEFAULT_POLICY = "developer";

function findPromptBox() {
  const candidates = [
    ...document.querySelectorAll("textarea"),
    ...document.querySelectorAll("[contenteditable='true']")
  ];
  return candidates.filter((element) => {
    const rect = element.getBoundingClientRect();
    return rect.width > 240 && rect.height > 24;
  }).at(-1);
}

function readPrompt(element) {
  if (!element) return "";
  if ("value" in element) return element.value || "";
  return element.innerText || element.textContent || "";
}

function writePrompt(element, value) {
  if (!element) return;
  if ("value" in element) {
    element.value = value;
    element.dispatchEvent(new Event("input", { bubbles: true }));
    return;
  }
  element.textContent = value;
  element.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: value }));
}

function showPanel(result, promptBox) {
  let panel = document.getElementById("shadowai-panel");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "shadowai-panel";
    document.body.appendChild(panel);
  }
  const decision = result.policy_decision || {};
  panel.className = `shadowai-panel shadowai-${decision.action || "allow"}`;
  panel.innerHTML = `
    <div class="shadowai-title">ShadowAI Guardian: ${(decision.action || "allow").toUpperCase()}</div>
    <div class="shadowai-meta">Risk ${result.risk_score}/100 • ${result.risk_level} • ${decision.policy_mode || "Developer"}</div>
    <div class="shadowai-body">${(decision.reasons || []).slice(0, 3).join("<br>")}</div>
    <div class="shadowai-actions">
      ${result.safe_text ? "<button id=\"shadowai-use-safe\">Use safe prompt</button>" : ""}
      <button id="shadowai-close">Close</button>
    </div>
  `;
  panel.querySelector("#shadowai-close")?.addEventListener("click", () => panel.remove());
  panel.querySelector("#shadowai-use-safe")?.addEventListener("click", () => {
    writePrompt(promptBox, result.safe_text);
    panel.remove();
  });
}

async function inspectPrompt() {
  const promptBox = findPromptBox();
  const text = readPrompt(promptBox).trim();
  if (!text) {
    showPanel({
      risk_score: 0,
      risk_level: "Safe",
      policy_decision: { action: "allow", policy_mode: "Developer", reasons: ["No prompt text found on this page"] }
    }, promptBox);
    return;
  }
  try {
    const response = await fetch(SHADOWAI_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, policy_mode: DEFAULT_POLICY, page_url: location.href })
    });
    if (!response.ok) throw new Error(`Local proxy returned ${response.status}`);
    showPanel(await response.json(), promptBox);
  } catch (error) {
    showPanel({
      risk_score: 0,
      risk_level: "Unknown",
      policy_decision: { action: "warn", policy_mode: "Developer", reasons: [`Local backend is not reachable: ${error.message}`] }
    }, promptBox);
  }
}

function mountButton() {
  if (document.getElementById("shadowai-inspect")) return;
  const button = document.createElement("button");
  button.id = "shadowai-inspect";
  button.type = "button";
  button.textContent = "Inspect with ShadowAI";
  button.addEventListener("click", inspectPrompt);
  document.body.appendChild(button);
}

mountButton();
new MutationObserver(mountButton).observe(document.body, { childList: true, subtree: true });
