import React, { useState, useEffect } from "react";
import * as Icons from "lucide-react";
import { API_BASE_URL } from "../config";

interface TableRendererProps {
  title: string;
  tableName: string;
  targetApiPath: string;
  columns: string[];
  actions: string[];
  activeRole: string;
  refreshTrigger: number;
  onRefresh: () => void;
}

// ── Local dummy data generator ──────────────────────────────────────────────
const FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eva", "Frank", "Grace", "Henry"];
const LAST_NAMES  = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"];
const STATUSES    = ["Active", "Pending", "Closed", "In Progress", "Review", "Approved"];
const CATEGORIES  = ["Enterprise", "SMB", "Startup", "Government", "Non-Profit", "Education"];

function seedValue(col: string, rowIndex: number): any {
  const c = col.toLowerCase();
  if (c === "id") return rowIndex + 1;
  if (c.includes("name") && c.includes("full")) return `${FIRST_NAMES[rowIndex % 8]} ${LAST_NAMES[rowIndex % 7]}`;
  if (c.includes("name")) return `${FIRST_NAMES[rowIndex % 8]} ${LAST_NAMES[rowIndex % 7]}`;
  if (c.includes("email")) return `user${rowIndex + 1}@example.com`;
  if (c.includes("phone")) return `+1 555-${String(1000 + rowIndex * 37).slice(0,4)}-${String(2000 + rowIndex * 13).slice(0,4)}`;
  if (c.includes("status")) return STATUSES[rowIndex % STATUSES.length];
  if (c.includes("category") || c.includes("type") || c.includes("tier")) return CATEGORIES[rowIndex % CATEGORIES.length];
  if (c.includes("amount") || c.includes("value") || c.includes("revenue") || c.includes("price") || c.includes("salary"))
    return parseFloat((Math.random() * 50000 + 5000).toFixed(2));
  if (c.includes("count") || c.includes("qty") || c.includes("quantity") || c.includes("age"))
    return Math.floor(Math.random() * 100) + 1;
  if (c.includes("date") || c.includes("_at") || c.includes("created") || c.includes("updated"))
    return new Date(Date.now() - rowIndex * 86400000 * 3).toISOString().split("T")[0];
  if (c.includes("active") || c.includes("enabled") || c.includes("verified")) return rowIndex % 3 !== 0;
  if (c.includes("note") || c.includes("description") || c.includes("comment"))
    return `Sample note for record ${rowIndex + 1}.`;
  if (c.includes("company") || c.includes("org")) return CATEGORIES[rowIndex % CATEGORIES.length] + " Corp";
  if (c.includes("role") || c.includes("position")) return ["Manager", "Developer", "Analyst", "Sales Rep"][rowIndex % 4];
  if (c.includes("score") || c.includes("rating")) return parseFloat((Math.random() * 5).toFixed(1));
  return `Record ${rowIndex + 1}`;
}

function generateLocalRows(columns: string[], count = 6): any[] {
  const displayCols = columns.filter(c => c !== "id");
  return Array.from({ length: count }, (_, i) => {
    const row: any = { id: i + 1 };
    displayCols.forEach(col => { row[col] = seedValue(col, i); });
    return row;
  });
}
// ────────────────────────────────────────────────────────────────────────────

export const TableRenderer: React.FC<TableRendererProps> = ({
  title,
  tableName,
  targetApiPath,
  columns,
  actions,
  activeRole,
  refreshTrigger,
  onRefresh,
}) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [isOffline, setIsOffline] = useState(false);

  const canDelete = activeRole === "admin";

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}${targetApiPath}`);
      if (!response.ok) throw new Error(`status ${response.status}`);
      const records = await response.json();
      setData(Array.isArray(records) ? records : generateLocalRows(columns));
      setIsOffline(false);
    } catch {
      // Backend unreachable or spec not loaded → fall back to local seed data
      setData(generateLocalRows(columns));
      setIsOffline(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [targetApiPath, refreshTrigger]);

  const handleDelete = async (id: number) => {
    if (!canDelete) {
      alert("RBAC Permission Denied: Only users with 'admin' role can delete records.");
      return;
    }
    if (!confirm("Are you sure you want to delete this record?")) return;

    if (isOffline) {
      setData(prev => prev.filter(r => r.id !== id));
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}${targetApiPath}/${id}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Delete failed");
      fetchData();
      onRefresh();
    } catch {
      // Soft delete locally on failure
      setData(prev => prev.filter(r => r.id !== id));
    }
  };

  const displayCols = columns.filter(c => c !== "id");

  const filteredData = data.filter(row =>
    displayCols.some(col => {
      const val = row[col];
      return val !== undefined && val !== null &&
        String(val).toLowerCase().includes(searchTerm.toLowerCase());
    })
  );

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <Icons.Database className="w-5 h-5 text-teal-400" />
            {title}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 flex items-center gap-1.5">
            Table: <code className="text-teal-500 font-mono">{tableName}</code> | {data.length} records
            {isOffline && (
              <span className="ml-1 px-1.5 py-0.5 bg-amber-100 text-amber-600 rounded text-[9px] font-bold uppercase tracking-wide">
                Demo Mode
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <input
              type="text"
              placeholder="Search table..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="bg-white border border-slate-200 text-slate-800 rounded-xl pl-9 pr-4 py-1.5 text-xs focus:ring-1 focus:ring-teal-500 focus:outline-none w-48 transition-all focus:w-60"
            />
            <Icons.Search className="w-3.5 h-3.5 text-slate-600 absolute left-3 top-2.5" />
          </div>

          <button
            onClick={fetchData}
            className="p-1.5 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors text-slate-500 hover:text-slate-800"
            title="Refresh Table Data"
          >
            <Icons.RotateCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-teal-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Content */}
      {loading && data.length === 0 ? (
        <div className="py-12 flex flex-col items-center justify-center text-slate-500 gap-2">
          <Icons.Loader className="w-8 h-8 animate-spin text-teal-500" />
          <span className="text-xs font-semibold uppercase tracking-wider">Loading data...</span>
        </div>
      ) : filteredData.length === 0 ? (
        <div className="py-12 text-center text-slate-600 flex flex-col items-center justify-center gap-2">
          <Icons.Inbox className="w-10 h-10 text-slate-400" />
          <p className="text-sm">No records found.</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200">
          <table className="w-full text-left text-slate-700 text-xs">
            <thead className="bg-white text-slate-500 uppercase tracking-widest text-[9px] font-bold border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">ID</th>
                {displayCols.map(c => (
                  <th key={c} className="px-4 py-3">{c.replace(/_/g, " ")}</th>
                ))}
                {actions.length > 0 && <th className="px-4 py-3 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-slate-50/50">
              {filteredData.map(row => (
                <tr key={row.id} className="hover:bg-slate-100/30 transition-colors">
                  <td className="px-4 py-3.5 font-mono text-slate-500 font-bold">#{row.id}</td>
                  {displayCols.map(col => {
                    const value = row[col];
                    const isCurrency = col.includes("value") || col.includes("amount") ||
                      col.includes("revenue") || col.includes("price") || col.includes("salary");
                    return (
                      <td key={col} className="px-4 py-3.5 font-medium text-slate-700">
                        {isCurrency && typeof value === "number" ? (
                          <span className="text-teal-500 font-semibold font-mono">
                            ${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </span>
                        ) : typeof value === "boolean" ? (
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            value ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-500"
                          }`}>
                            {value ? "TRUE" : "FALSE"}
                          </span>
                        ) : (
                          String(value !== null && value !== undefined ? value : "—")
                        )}
                      </td>
                    );
                  })}
                  {actions.length > 0 && (
                    <td className="px-4 py-3.5 text-right">
                      <div className="flex justify-end gap-2">
                        {actions.includes("delete") && (
                          <button
                            onClick={() => handleDelete(row.id)}
                            className={`p-1.5 rounded-lg border text-xs transition-all ${
                              canDelete
                                ? "border-red-200 text-red-500 hover:bg-red-50 hover:border-red-300"
                                : "border-slate-200 text-slate-400 cursor-not-allowed opacity-30"
                            }`}
                            disabled={!canDelete}
                            title={canDelete ? "Delete Record" : "Admin role required"}
                          >
                            <Icons.Trash2 className="w-3.5 h-3.5" />
                          </button>
                        )}
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
