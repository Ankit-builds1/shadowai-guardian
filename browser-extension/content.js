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

function createPanel(className) {
  let panel = document.getElementById("shadowai-panel");
  if (!panel) {
    panel = document.createElement("div");
    panel.id = "shadowai-panel";
    document.body.appendChild(panel);
  }
  panel.replaceChildren();
  panel.className = className;
  return panel;
}

function appendPanelText(panel, className, text) {
  const element = document.createElement("div");
  element.className = className;
  element.textContent = String(text ?? "");
  panel.appendChild(element);
  return element;
}

function appendPanelButton(actions, id, text, handler) {
  const button = document.createElement("button");
  button.id = id;
  button.type = "button";
  button.textContent = text;
  button.addEventListener("click", handler);
  actions.appendChild(button);
}

function showPanel(result, promptBox) {
  const decision = result.policy_decision || {};
  const action = decision.action || "allow";
  const panel = createPanel(`shadowai-panel shadowai-${action}`);
  appendPanelText(panel, "shadowai-title", `ShadowAI Guardian: ${action.toUpperCase()}`);
  appendPanelText(
    panel,
    "shadowai-meta",
    `Risk ${result.risk_score ?? 0}/100 | ${result.risk_level || "Unknown"} | ${decision.policy_mode || "Developer"}`
  );
  appendPanelText(panel, "shadowai-body", (decision.reasons || []).slice(0, 3).join("\n"));
  const actions = appendPanelText(panel, "shadowai-actions", "");
  if (result.safe_text) {
    appendPanelButton(actions, "shadowai-use-safe", "Use safe prompt", () => {
      writePrompt(promptBox, result.safe_text);
      panel.remove();
    });
  }
  appendPanelButton(actions, "shadowai-close", "Close", () => panel.remove());
}

function showRepoPanel(result) {
  const isError = Boolean(result.error);
  const state = isError ? "warn" : result.risk_level === "Safe" ? "allow" : "block";
  const panel = createPanel(`shadowai-panel shadowai-${state}`);
  appendPanelText(
    panel,
    "shadowai-title",
    `ShadowAI Repo Scan: ${isError ? "WARN" : result.risk_level || "Unknown"}`
  );
  appendPanelText(panel, "shadowai-meta", result.repo_name || "GitHub repository");
  const body = isError
    ? result.error
    : `${result.files_scanned} files scanned\n${result.secrets_found} secrets found\nRisk ${result.risk_score}/100`;
  appendPanelText(panel, "shadowai-body", body);
  const actions = appendPanelText(panel, "shadowai-actions", "");
  appendPanelButton(actions, "shadowai-close", "Close", () => panel.remove());
}

async function scanGitHubRepo() {
  const repoUrl = getGitHubRepoUrl(location.href);
  if (!repoUrl) {
    showRepoPanel({ error: "Open a GitHub repository page to scan it." });
    return;
  }
  showRepoPanel({ repo_name: repoUrl, risk_level: "Scanning", files_scanned: "Scanning", secrets_found: "Scanning", risk_score: 0 });
  try {
    const response = await chrome.runtime.sendMessage({
      type: "SHADOWAI_SCAN_REPO",
      payload: { repo_url: repoUrl }
    });
    if (!response?.ok) throw new Error(response?.error || "Local repo scanner did not respond");
    showRepoPanel(response.data);
  } catch (error) {
    showRepoPanel({ repo_name: repoUrl, error: `Local backend is not reachable: ${error.message}` });
  }
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
    const response = await chrome.runtime.sendMessage({
      type: "SHADOWAI_INSPECT",
      payload: { text, policy_mode: DEFAULT_POLICY, page_url: location.href }
    });
    if (!response?.ok) throw new Error(response?.error || "Local proxy did not respond");
    showPanel(response.data, promptBox);
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
  const isGitHubRepo = Boolean(getGitHubRepoUrl(location.href));
  button.textContent = isGitHubRepo ? "Scan Repo with ShadowAI" : "Inspect with ShadowAI";
  button.addEventListener("click", isGitHubRepo ? scanGitHubRepo : inspectPrompt);
  document.body.appendChild(button);
}

mountButton();
new MutationObserver(mountButton).observe(document.body, { childList: true, subtree: true });
