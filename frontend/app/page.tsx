import Link from "next/link";
import { Bot, FileSearch, Github, ShieldCheck } from "lucide-react";

export default function Page() {
  const features = [
    [ShieldCheck, "Prompt Firewall", "Detect secrets and personal data before prompts leave your machine."],
    [FileSearch, "Document Scanner", "Inspect PDFs, DOCX, and text files for risky content."],
    [Github, "Repo Secret Scan", "Find credentials in public or local-friendly repositories."],
    [Bot, "Privacy Agent", "Run a seven-step agentic review before approval."]
  ];
  return (
    <div className="space-y-8">
      <section className="rounded-lg bg-slate-950 p-12 text-white">
        <h1 className="text-5xl font-bold">ShadowAI Guardian</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-300">Protect sensitive data before it reaches AI tools. Runs 100% locally.</p>
        <Link href="/scanner" className="btn mt-8 bg-white text-slate-950 hover:bg-slate-200">Open Scanner</Link>
      </section>
      <div className="grid gap-4 md:grid-cols-4">
        {features.map(([Icon, title, body]: any) => <div key={title} className="card"><Icon className="mb-3 h-6 w-6 text-blue-600" /><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm text-slate-600">{body}</p></div>)}
      </div>
    </div>
  );
}
