"use client";

import { Globe } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import { RiskBadge } from "../../components/RiskBadge";

export default function ToolRiskPage() {
  const [domain, setDomain] = useState("");
  const [result, setResult] = useState<any>(null);
  async function check() {
    try {
      const res = await api.post("/api/tool-risk", { domain });
      setResult(res.data);
    } catch {
      toast.error("Tool check failed");
    }
  }
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="card">
        <h1 className="mb-4 flex items-center gap-2 text-2xl font-bold"><Globe /> AI Tool Trust Checker</h1>
        <div className="flex gap-3"><input className="input" placeholder="chat.openai.com" value={domain} onChange={(e) => setDomain(e.target.value)} /><button className="btn" onClick={check}>Check Trust</button></div>
      </div>
      {result && <div className="card space-y-4"><div className="flex items-center justify-between"><h2 className="text-xl font-bold">{result.tool_name || result.domain}</h2><RiskBadge level={result.risk_level} /></div><p>Trust: <b>{result.user_trust_status}</b></p><p>HTTPS: <b>{result.is_https ? "Enabled" : "Missing"}</b></p><div className="h-3 rounded bg-slate-200"><div className="h-3 rounded bg-blue-600" style={{ width: `${result.risk_score}%` }} /></div><p className="text-sm text-slate-600">{result.recommendation}</p></div>}
    </div>
  );
}
