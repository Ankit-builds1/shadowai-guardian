"use client";

import Link from "next/link";
import { AlertTriangle } from "lucide-react";
import EntityCard from "./EntityCard";
import { RiskBadge } from "./RiskBadge";
import SafePromptBox from "./SafePromptBox";

export default function ScanResult({ result, safeText, onRewrite }: { result: any; safeText?: string; onRewrite?: () => void }) {
  if (!result) return null;
  const color = result.risk_score > 80 ? "text-red-600" : result.risk_score > 60 ? "text-orange-600" : result.risk_score > 40 ? "text-yellow-600" : result.risk_score > 0 ? "text-blue-600" : "text-green-600";
  return (
    <div className="space-y-4">
      <div className="card">
        <div className="flex items-center justify-between">
          <div className={`text-6xl font-bold ${color}`}>{result.risk_score}</div>
          <RiskBadge level={result.risk_level} />
        </div>
        <p className="mt-2 text-sm text-slate-600">{result.category}</p>
      </div>
      {result.injection_detected && <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-800"><AlertTriangle className="mr-2 inline h-4 w-4" /> Prompt Injection Attack Detected: {result.injection?.matched_patterns?.join(", ")}</div>}
      <div className="card">
        <h3 className="mb-3 font-semibold">Detected Entities</h3>
        <div className="grid gap-3">{result.entities?.length ? result.entities.map((e: any, i: number) => <EntityCard key={i} entity={e} />) : <p className="text-sm text-slate-500">No entities detected.</p>}</div>
      </div>
      {safeText && <SafePromptBox text={safeText} />}
      <div className="card">
        <h3 className="mb-2 font-semibold">Explanation</h3>
        <p className="text-sm leading-6 text-slate-700">{result.explanation}</p>
      </div>
      <div className="flex gap-3">
        {onRewrite && <button className="btn" onClick={onRewrite}>Get Safe Version</button>}
        <Link className="btn" href="/agent">Run AI Agent</Link>
      </div>
    </div>
  );
}
