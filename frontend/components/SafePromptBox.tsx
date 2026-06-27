"use client";

import { Copy } from "lucide-react";
import toast from "react-hot-toast";

export default function SafePromptBox({ text }: { text: string }) {
  return (
    <div className="rounded-md border border-green-200 bg-green-50 p-4">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="font-semibold text-green-900">Safe Version</h3>
        <button className="btn" onClick={() => navigator.clipboard.writeText(text).then(() => toast.success("Copied"))}><Copy className="h-4 w-4" /> Copy</button>
      </div>
      <pre className="whitespace-pre-wrap text-sm text-slate-800">{text}</pre>
    </div>
  );
}
