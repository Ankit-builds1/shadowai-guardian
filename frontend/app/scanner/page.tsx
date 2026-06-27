"use client";

import { Loader2, Search } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import ScanResult from "../../components/ScanResult";

export default function ScannerPage() {
  const [text, setText] = useState("");
  const [targetTool, setTargetTool] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [safeText, setSafeText] = useState("");
  async function scan() {
    setLoading(true);
    try {
      const res = await api.post("/api/scan/prompt", { text, target_tool: targetTool, source_type: "prompt" });
      setResult(res.data);
      setSafeText("");
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
        <h1 className="text-2xl font-bold">Prompt Scanner</h1>
        <textarea className="input min-h-72" placeholder="Paste your prompt, code, or text here..." value={text} onChange={(e) => setText(e.target.value)} />
        <input className="input" placeholder="e.g. chat.openai.com" value={targetTool} onChange={(e) => setTargetTool(e.target.value)} />
        <button className="btn w-full" disabled={loading || !text} onClick={scan}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Scan Now</button>
      </div>
      <ScanResult result={result} safeText={safeText} onRewrite={rewrite} />
    </div>
  );
}
