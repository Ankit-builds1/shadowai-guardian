"use client";

import { Loader2, Search } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import ScanResult from "../../components/ScanResult";

export default function ScannerPage() {
  const [text, setText] = useState("");
  const [policyMode, setPolicyMode] = useState("developer");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [safeText, setSafeText] = useState("");
  async function scan() {
    setLoading(true);
    try {
      const res = await api.post("/api/proxy/inspect", { text, policy_mode: policyMode });
      setResult(res.data);
      setSafeText(res.data.safe_text || "");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Scan failed");
    } finally {
      setLoading(false);
    }
  }
  async function rewrite() {
    const res = await api.post("/api/rewrite", { text, entities: result.entities });
    setSafeText(res.data.safe_text);
  }
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div className="card space-y-4">
        <div>
          <h1 className="text-2xl font-bold">Prompt Firewall</h1>
          <p className="mt-1 text-sm text-slate-600">Inspect prompts with the same local policy engine used by the browser extension.</p>
        </div>
        <textarea className="input min-h-72" placeholder="Paste your prompt, code, or text here..." value={text} onChange={(e) => setText(e.target.value)} />
        <select className="input" value={policyMode} onChange={(e) => setPolicyMode(e.target.value)}>
          <option value="student">Student Mode</option>
          <option value="developer">Developer Mode</option>
          <option value="company">Company Mode</option>
          <option value="strict">Strict Compliance</option>
        </select>
        <button className="btn w-full" disabled={loading || !text} onClick={scan}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Inspect Through Local Proxy</button>
        {result?.policy_decision && (
          <div className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm">
            <div className="font-semibold">Policy Decision: {result.policy_decision.action.toUpperCase()}</div>
            <div className="mt-1 text-slate-600">{result.policy_decision.policy_mode}</div>
            <ul className="mt-2 list-disc pl-5 text-slate-700">
              {result.policy_decision.reasons.map((reason: string) => <li key={reason}>{reason}</li>)}
            </ul>
          </div>
        )}
      </div>
      <ScanResult result={result} safeText={safeText} onRewrite={rewrite} />
    </div>
  );
}
