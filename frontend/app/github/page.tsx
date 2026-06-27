"use client";

import { Github, Loader2 } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import { RiskBadge, SeverityBadge } from "../../components/RiskBadge";

export default function GithubPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  async function scan() {
    setLoading(true);
    try {
      const res = await api.post("/api/scan/github", { repo_url: repoUrl });
      setResult(res.data);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Repository scan failed");
    } finally {
      setLoading(false);
    }
  }
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="mb-4 flex items-center gap-2 text-2xl font-bold"><Github /> Repo Secret Scanner</h1>
        <div className="flex gap-3"><input className="input" placeholder="https://github.com/org/repo" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)} /><button className="btn" onClick={scan} disabled={loading || !repoUrl}>{loading && <Loader2 className="h-4 w-4 animate-spin" />} Scan Repository</button></div>
        {loading && <p className="mt-3 text-sm text-slate-500">Cloning... Scanning files... Analyzing...</p>}
      </div>
      {result && <div className="card"><div className="mb-4 flex items-center gap-6"><span>{result.files_scanned} files scanned</span><span>{result.secrets_found} secrets found</span><RiskBadge level={result.risk_level} /></div><table className="w-full text-sm"><thead><tr className="text-left"><th>File</th><th>Line</th><th>Type</th><th>Severity</th></tr></thead><tbody>{result.findings.map((f: any, i: number) => <tr className="border-t" key={i}><td className="py-2">{f.file_path}</td><td>{f.line_number}</td><td>{f.entity_type}</td><td><SeverityBadge severity={f.severity} /></td></tr>)}</tbody></table></div>}
    </div>
  );
}
