"use client";

import clsx from "clsx";

const classes: Record<string, string> = {
  Critical: "bg-red-100 text-red-700 border-red-300",
  critical: "bg-red-100 text-red-700 border-red-300",
  High: "bg-orange-100 text-orange-700 border-orange-300",
  high: "bg-orange-100 text-orange-700 border-orange-300",
  Medium: "bg-yellow-100 text-yellow-700 border-yellow-300",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-300",
  Low: "bg-blue-100 text-blue-700 border-blue-300",
  low: "bg-blue-100 text-blue-700 border-blue-300",
  Safe: "bg-green-100 text-green-700 border-green-300",
  safe: "bg-green-100 text-green-700 border-green-300"
};

export function RiskBadge({ level }: { level: string }) {
  return <span className={clsx("rounded-full border px-2.5 py-1 text-xs font-semibold", classes[level] || "bg-slate-100 text-slate-700 border-slate-300")}>{level}</span>;
}

export function SeverityBadge({ severity }: { severity: string }) {
  return <RiskBadge level={severity.charAt(0).toUpperCase() + severity.slice(1)} />;
}
