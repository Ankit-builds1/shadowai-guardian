"use client";

import { Clipboard } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import ScanResult from "../../components/ScanResult";

export default function ClipboardPage() {
  const [result, setResult] = useState<any>(null);
  const [safeText, setSafeText] = useState("");
  async function scanClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      const res = await api.post("/api/scan/prompt", { text, source_type: "clipboard" });
      setResult(res.data);
      const rewrite = await api.post("/api/rewrite", { text, entities: res.data.entities });
      setSafeText(rewrite.data.safe_text);
    } catch {
      toast.error("Clipboard permission denied or scan failed");
    }
  }
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="card text-center">
        <Clipboard className="mx-auto mb-4 h-10 w-10 text-blue-600" />
        <h1 className="text-2xl font-bold">Clipboard Scanner</h1>
        <p className="mt-2 text-slate-600">Read your clipboard with browser permission and scan it locally through the backend.</p>
        <button className="btn mt-5" onClick={scanClipboard}>Scan My Clipboard</button>
      </div>
      {result?.risk_level !== "Safe" && result && <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-800">Risky clipboard content detected. Use the safe version below.</div>}
      <ScanResult result={result} safeText={safeText} />
    </div>
  );
}
