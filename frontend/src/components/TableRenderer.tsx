import React, { useState, useEffect } from "react";
import * as Icons from "lucide-react";

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
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const canDelete = activeRole === "admin";

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000${targetApiPath}`);
      if (!response.ok) {
        throw new Error(`Failed to load dynamic table. Server responded with status ${response.status}`);
      }
      const records = await response.json();
      setData(records);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [targetApiPath, refreshTrigger]);

  const handleDelete = async (id: number) => {
    if (!canDelete) {
      alert("RBAC Permission Denied: Only users with 'admin' role can delete records from this dynamic table.");
      return;
    }

    if (!confirm("Are you sure you want to delete this compiled record?")) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000${targetApiPath}/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete record.");
      }

      fetchData(); // Reload table
      onRefresh(); // Trigger dashboard counters/charts refresh!
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Filter columns to exclude 'id' from primary layout if desired, but keep for action triggers
  const displayCols = columns.filter((c) => c !== "id");

  const filteredData = data.filter((row) => {
    return displayCols.some((col) => {
      const val = row[col];
      return val !== undefined && val !== null && String(val).toLowerCase().includes(searchTerm.toLowerCase());
    });
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      {/* 1. Header Area with dynamic count & Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
        <div>
          <h3 className="text-lg font-bold text-slate-200 flex items-center gap-2">
            <Icons.Database className="w-5 h-5 text-teal-400" />
            {title}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Table: <code className="text-teal-500 font-mono">{tableName}</code> | {data.length} records
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Search bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search table..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 rounded-xl pl-9 pr-4 py-1.5 text-xs focus:ring-1 focus:ring-teal-500 focus:outline-none w-48 transition-all focus:w-60"
            />
            <Icons.Search className="w-3.5 h-3.5 text-slate-600 absolute left-3 top-2.5" />
          </div>

          <button
            onClick={fetchData}
            className="p-1.5 hover:bg-slate-800 rounded-lg border border-slate-800 transition-colors text-slate-400 hover:text-slate-200"
            title="Refresh Table Data"
          >
            <Icons.RotateCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-teal-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* 2. Content / Loader */}
      {loading && data.length === 0 ? (
        <div className="py-12 flex flex-col items-center justify-center text-slate-500 gap-2">
          <Icons.Loader className="w-8 h-8 animate-spin text-teal-500" />
          <span className="text-xs font-semibold uppercase tracking-wider">Fetching dynamic database...</span>
        </div>
      ) : error ? (
        <div className="py-10 text-center text-red-400 border border-red-900/30 bg-red-950/15 rounded-2xl flex flex-col items-center justify-center gap-2">
          <Icons.ShieldAlert className="w-8 h-8 text-red-500" />
          <p className="text-sm font-semibold">{error}</p>
          <button onClick={fetchData} className="text-xs underline text-slate-400 hover:text-slate-200">
            Retry Connection
          </button>
        </div>
      ) : filteredData.length === 0 ? (
        <div className="py-12 text-center text-slate-600 flex flex-col items-center justify-center gap-2">
          <Icons.Inbox className="w-10 h-10 text-slate-700" />
          <p className="text-sm">No records found matching table indices.</p>
        </div>
      ) : (
        /* 3. Table UI */
        <div className="overflow-x-auto rounded-xl border border-slate-850">
          <table className="w-full text-left text-slate-300 text-xs">
            <thead className="bg-slate-950 text-slate-500 uppercase tracking-widest text-[9px] font-bold border-b border-slate-850">
              <tr>
                <th className="px-4 py-3">ID</th>
                {displayCols.map((c) => (
                  <th key={c} className="px-4 py-3">
                    {c.replace("_", " ")}
                  </th>
                ))}
                {actions.length > 0 && <th className="px-4 py-3 text-right">Actions</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-850 bg-slate-900/50">
              {filteredData.map((row) => (
                <tr key={row.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3.5 font-mono text-slate-500 font-bold">#{row.id}</td>
                  {displayCols.map((col) => {
                    const value = row[col];
                    const isCurrency = col.includes("value") || col.includes("amount") || col.includes("impact");
                    return (
                      <td key={col} className="px-4 py-3.5 font-medium text-slate-300">
                        {isCurrency && typeof value === "number" ? (
                          <span className="text-teal-400 font-semibold font-mono">
                            ${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                          </span>
                        ) : typeof value === "boolean" ? (
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                              value ? "bg-emerald-950 text-emerald-400" : "bg-red-950/55 text-red-400"
                            }`}
                          >
                            {value ? "TRUE" : "FALSE"}
                          </span>
                        ) : (
                          String(value !== null && value !== undefined ? value : "-")
                        )}
                      </td>
                    );
                  })}
                  {actions.length > 0 && (
                    <td className="px-4 py-3.5 text-right flex justify-end gap-2">
                      {actions.includes("delete") && (
                        <button
                          onClick={() => handleDelete(row.id)}
                          className={`p-1.5 rounded-lg border text-xs transition-all ${
                            canDelete
                              ? "border-red-900/40 text-red-500 hover:bg-red-950/20 hover:border-red-800"
                              : "border-slate-800 text-slate-700 cursor-not-allowed opacity-30"
                          }`}
                          disabled={!canDelete}
                          title={canDelete ? "Delete Record" : "RBAC Admin role required"}
                        >
                          <Icons.Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
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
