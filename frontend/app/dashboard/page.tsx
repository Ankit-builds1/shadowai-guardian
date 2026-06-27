"use client";

import { useEffect, useState } from "react";
import { Area, AreaChart, Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../../components/api";
import { RiskBadge } from "../../components/RiskBadge";

const colors: any = { Safe: "#22c55e", Low: "#3b82f6", Medium: "#eab308", High: "#f97316", Critical: "#ef4444" };

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  useEffect(() => { api.get("/api/dashboard/stats").then((r) => setStats(r.data)); }, []);
  if (!stats) return <div className="card">Loading dashboard...</div>;
  const score = stats.privacy_amnesia_score;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Risk Timeline</h1>
        <p className="mt-1 text-sm text-slate-600">Track prevented leaks, prompt risk, and privacy score improvement over time.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {[["Total Scans", stats.total_scans], ["Critical Alerts", stats.critical_alerts], ["Injection Attacks", stats.injection_attacks_total], ["Average Risk Score", `${stats.average_risk_score}/100`]].map(([k, v]) => <div className="card" key={k}><div className="text-sm text-slate-500">{k}</div><div className="mt-2 text-3xl font-bold">{v}</div></div>)}
      </div>
      <div className="card grid gap-6 md:grid-cols-3">
        <div className="text-center"><div className="text-8xl font-bold" style={{ color: score.color }}>{score.grade}</div><div className="text-xl font-semibold">{score.score} / 100</div></div>
        <div><h2 className="text-xl font-bold">Privacy Score</h2><p className="mt-2 text-slate-600">{score.label}</p><p className={score.trend === "up" ? "mt-3 text-green-600" : "mt-3 text-red-600"}>{score.trend === "up" ? "Up" : score.trend === "down" ? "Down" : "Flat"} {score.improvement_percent} pts from last month</p></div>
        <div className="grid grid-cols-2 gap-2 text-sm">{Object.entries(score.counts).map(([k, v]: any) => <div className="rounded border p-3" key={k}><b>{v}</b><br />{k}</div>)}</div>
      </div>
      <div className="card h-80">
        <h2 className="mb-4 font-semibold">7-Day Risk Timeline</h2>
        <ResponsiveContainer>
          <AreaChart data={stats.risk_timeline}>
            <XAxis dataKey="date" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Area type="monotone" dataKey="average_risk" stroke="#2563eb" fill="#bfdbfe" name="Average Risk" />
            <Area type="monotone" dataKey="critical" stroke="#ef4444" fill="#fecaca" name="Critical Findings" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <div className="card h-80"><h2 className="mb-4 font-semibold">Risk Distribution</h2><ResponsiveContainer><BarChart data={stats.risk_distribution}><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="value">{stats.risk_distribution.map((e: any) => <Cell key={e.name} fill={colors[e.name]} />)}</Bar></BarChart></ResponsiveContainer></div>
        <div className="card h-80"><h2 className="mb-4 font-semibold">Entity Types</h2><ResponsiveContainer><PieChart><Pie data={stats.entity_breakdown.length ? stats.entity_breakdown : [{ name: "None", value: 1 }]} dataKey="value" nameKey="name" outerRadius={95}>{(stats.entity_breakdown.length ? stats.entity_breakdown : [{ name: "None" }]).map((_: any, i: number) => <Cell key={i} fill={["#2563eb", "#14b8a6", "#eab308", "#ef4444"][i % 4]} />)}</Pie><Tooltip /></PieChart></ResponsiveContainer></div>
      </div>
      <div className="card"><h2 className="mb-4 font-semibold">Recent Scans</h2><table className="w-full text-sm"><thead><tr className="text-left"><th>Time</th><th>Source</th><th>Risk Level</th><th>Category</th><th>Score</th></tr></thead><tbody>{stats.recent_scans.map((s: any) => <tr className="border-t" key={s.id}><td className="py-2">{new Date(s.created_at).toLocaleString()}</td><td>{s.source_type}</td><td><RiskBadge level={s.risk_level} /></td><td>{s.category}</td><td>{s.risk_score}</td></tr>)}</tbody></table></div>
    </div>
  );
}
