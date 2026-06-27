"use client";

import { Copy, Download, FileText } from "lucide-react";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import { RiskBadge } from "../../components/RiskBadge";

const tabs = ["All", "Critical", "High", "Medium", "Low", "Safe"];
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [tab, setTab] = useState("All");
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    api.get("/api/reports").then((response) => setReports(response.data));
  }, []);

  const filtered = tab === "All" ? reports : reports.filter((report) => report.risk_level === tab);

  function pdfUrl(report: any) {
    return `${apiBaseUrl}/api/reports/${report.id}/pdf`;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reports</h1>
        <p className="mt-1 text-sm text-slate-600">
          Review scan history and export detailed local PDF reports for audit or handoff.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button
            className={`rounded-md px-3 py-2 text-sm ${tab === item ? "bg-slate-900 text-white" : "border bg-white"}`}
            key={item}
            onClick={() => setTab(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="grid gap-4">
        {filtered.map((report) => (
          <div className="card" key={report.id}>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <b>{new Date(report.created_at).toLocaleString()}</b>
                <p className="mt-1 text-sm text-slate-500">
                  {report.source_type} · {report.category} · {report.risk_score}/100
                </p>
              </div>
              <RiskBadge level={report.risk_level} />
            </div>

            <div className="mt-4 flex flex-wrap gap-3">
              <button className="btn" onClick={() => setOpen(open === report.id ? null : report.id)}>
                <FileText className="h-4 w-4" /> View Details
              </button>
              <a className="btn bg-slate-900 hover:bg-slate-800" href={pdfUrl(report)} download={`shadowai-report-${report.id}.pdf`}>
                <Download className="h-4 w-4" /> Download PDF
              </a>
            </div>

            {open === report.id && (
              <div className="mt-5 space-y-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div>
                  <h2 className="font-semibold">Analysis</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-700">{report.explanation}</p>
                </div>

                <div>
                  <h2 className="font-semibold">Detected Entities</h2>
                  {report.entities.length ? (
                    <div className="mt-2 overflow-hidden rounded-md border border-slate-200 bg-white">
                      <table className="w-full text-sm">
                        <thead className="bg-slate-100 text-left text-slate-600">
                          <tr>
                            <th className="p-3">Type</th>
                            <th className="p-3">Severity</th>
                            <th className="p-3">Redacted Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {report.entities.map((entity: any, index: number) => (
                            <tr className="border-t" key={`${entity.entity_type}-${index}`}>
                              <td className="p-3 font-medium">{entity.entity_type}</td>
                              <td className="p-3">{entity.severity}</td>
                              <td className="break-all p-3 text-slate-600">{entity.redacted_value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-slate-600">No sensitive entities were detected.</p>
                  )}
                </div>

                <div className="flex flex-wrap gap-3">
                  <button
                    className="btn"
                    onClick={() => navigator.clipboard.writeText(report.markdown_report).then(() => toast.success("Report copied"))}
                  >
                    <Copy className="h-4 w-4" /> Copy Markdown
                  </button>
                  <a className="btn bg-slate-900 hover:bg-slate-800" href={pdfUrl(report)} download={`shadowai-report-${report.id}.pdf`}>
                    <Download className="h-4 w-4" /> Download Detailed PDF
                  </a>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
