import { Download, FolderOpen, MonitorCheck, ShieldCheck } from "lucide-react";

export default function ExtensionPage() {
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="flex items-center gap-2 text-2xl font-bold"><MonitorCheck /> Browser Extension / Local Proxy</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Load the included Chrome extension to inspect prompts on AI websites before they are submitted.
          It calls only your local backend at localhost and uses the same policy engine as the Prompt Firewall.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="card"><FolderOpen className="mb-3 h-6 w-6 text-blue-600" /><h2 className="font-semibold">1. Open Extension Folder</h2><p className="mt-2 text-sm text-slate-600">Use Chrome Extensions developer mode and load the `browser-extension` folder from this project.</p></div>
        <div className="card"><ShieldCheck className="mb-3 h-6 w-6 text-green-600" /><h2 className="font-semibold">2. Keep Backend Running</h2><p className="mt-2 text-sm text-slate-600">The extension talks to `http://localhost:8000/api/proxy/inspect`.</p></div>
        <div className="card"><Download className="mb-3 h-6 w-6 text-slate-700" /><h2 className="font-semibold">3. Use Safe Copy</h2><p className="mt-2 text-sm text-slate-600">When risk is blocked, copy the redacted prompt instead of sending raw secrets.</p></div>
      </div>
      <div className="card">
        <h2 className="mb-3 font-semibold">Local Extension Path</h2>
        <code className="rounded bg-slate-100 px-3 py-2 text-sm">browser-extension</code>
      </div>
    </div>
  );
}
