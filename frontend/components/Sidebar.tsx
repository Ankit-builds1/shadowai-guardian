"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, Clipboard, FileBarChart, FileText, Github, Globe, LayoutDashboard, Search, ShieldAlert } from "lucide-react";
import clsx from "clsx";

const nav = [
  ["/dashboard", "Dashboard", LayoutDashboard],
  ["/scanner", "Scanner", Search],
  ["/clipboard", "Clipboard", Clipboard],
  ["/documents", "Documents", FileText],
  ["/github", "GitHub", Github],
  ["/tool-risk", "Tool Risk", Globe],
  ["/agent", "Agent", Bot],
  ["/reports", "Reports", FileBarChart]
] as const;

export default function Sidebar() {
  const path = usePathname();
  return (
    <aside className="fixed inset-y-0 left-0 z-20 flex w-64 flex-col border-r border-slate-200 bg-white">
      <Link href="/" className="flex h-16 items-center gap-3 border-b border-slate-200 px-5 font-bold">
        <ShieldAlert className="h-6 w-6 text-blue-600" /> ShadowAI Guardian
      </Link>
      <nav className="flex-1 space-y-1 p-3">
        {nav.map(([href, label, Icon]) => (
          <Link key={href} href={href} className={clsx("flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium", path === href ? "bg-slate-900 text-white" : "text-slate-700 hover:bg-slate-100")}>
            <Icon className="h-4 w-4" /> {label}
          </Link>
        ))}
      </nav>
      <div className="m-4 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-800">Privacy Score: local-first</div>
    </aside>
  );
}
