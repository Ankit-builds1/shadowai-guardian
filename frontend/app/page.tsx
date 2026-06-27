import Link from "next/link";
import { Activity, Github, MonitorCheck, ShieldCheck } from "lucide-react";

export default function Page() {
  const features = [
    [ShieldCheck, "Prompt Firewall", "Block secrets, PII, and prompt injection before AI submission."],
    [MonitorCheck, "Browser Proxy", "Inspect prompts from AI websites through a local extension."],
    [Github, "Repo Secret Scanner", "Find exposed credentials in public GitHub repositories."],
    [Activity, "Risk Timeline", "Track privacy score improvement and weekly risk behavior."]
  ];
  return (
    <div className="space-y-8">
      <section className="rounded-lg bg-slate-950 p-12 text-white">
        <h1 className="text-5xl font-bold">ShadowAI Guardian</h1>
        <p className="mt-4 max-w-2xl text-lg text-slate-300">A local-first AI safety proxy for prompts, browser usage, and repository secrets.</p>
        <Link href="/scanner" className="btn mt-8 bg-white text-slate-950 hover:bg-slate-200">Open Prompt Firewall</Link>
      </section>
      <div className="grid gap-4 md:grid-cols-4">
        {features.map(([Icon, title, body]: any) => <div key={title} className="card"><Icon className="mb-3 h-6 w-6 text-blue-600" /><h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm text-slate-600">{body}</p></div>)}
      </div>
    </div>
  );
}
