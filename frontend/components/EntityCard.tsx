import { SeverityBadge } from "./RiskBadge";

export default function EntityCard({ entity }: { entity: any }) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <div className="flex items-center justify-between">
        <span className="font-semibold">{entity.entity_type}</span>
        <SeverityBadge severity={entity.severity} />
      </div>
      <p className="mt-2 break-all text-xs text-slate-600">{entity.redacted_value}</p>
    </div>
  );
}
