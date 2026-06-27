"use client";

import { Bot } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";

export default function AgentPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [approved, setApproved] = useState("");
  useEffect(() => { api.get("/api/agent/audit").then((r) => setAudit(r.data)); }, [result]);
  async function run() {
    try {
      const res = await api.post("/api/agent/analyze", { text });
      setResult(res.data);
    } catch {
      toast.error("Agent analysis failed");
    }
  }
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="mb-4 flex items-center gap-2 text-2xl font-bold"><Bot /> Privacy Agent</h1>
        <textarea className="input min-h-44" value={text} onChange={(e) => setText(e.target.value)} />
        <button className="btn mt-4" disabled={!text} onClick={run}>Run Privacy Agent</button>
      </div>
      {result && <div className="space-y-4">{result.steps.map((s: any, i: number) => <div className="card animate-pulse" style={{ animationDelay: `${i * 120}ms` }} key={s.step}><div className="flex items-center gap-3"><span className="grid h-8 w-8 place-items-center rounded-full bg-blue-600 text-white">{s.step}</span><b>{s.name}</b><span className="text-xs text-slate-500">{new Date(s.timestamp).toLocaleTimeString()}</span></div><p className="mt-3 text-sm text-slate-700">{s.result}</p></div>)}<div className="card"><h2 className="text-xl font-bold">{result.decision}</h2><p className="mt-2">{result.suggested_action}</p><div className="mt-4 flex gap-3"><button className="btn bg-green-600 hover:bg-green-700" onClick={() => setApproved("Approved")}>Approve ✓</button><button className="btn bg-red-600 hover:bg-red-700" onClick={() => setApproved("Rejected")}>Reject ×</button></div>{approved && <p className="mt-3 font-semibold">{approved}</p>}</div></div>}
      <div className="card"><h2 className="mb-3 font-semibold">Audit Log</h2><table className="w-full text-sm"><tbody>{audit.map((a) => <tr className="border-t" key={a.id}><td className="py-2">{new Date(a.created_at).toLocaleString()}</td><td>{a.action}</td><td>{a.description}</td></tr>)}</tbody></table></div>
    </div>
  );
}
