import React, { useState, useEffect } from "react";
import * as Icons from "lucide-react";
import { API_BASE_URL } from "../config";

interface ChartRendererProps {
  id: string;
  type: "MetricCard" | "Chart";
  title: string;
  targetApiPath: string;
  gridSpan?: number;
  props: {
    operation: string;
    column: string;
    group_by?: string;
    label?: string;
    icon?: string;
    chart_type?: string;
    x_axis?: string;
    y_axis?: string;
    table_name?: string;
    target_table?: string;
  };
  refreshTrigger: number;
}

// ── Local fallback generators ────────────────────────────────────────────────
const CHART_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];
const CHART_COLORS = ["from-teal-500 to-indigo-500", "from-emerald-400 to-teal-500",
  "from-indigo-500 to-purple-500", "from-amber-400 to-orange-500",
  "from-pink-400 to-rose-500", "from-sky-400 to-blue-500"];

function generateDummyMetric(column: string): number {
  const c = column.toLowerCase();
  if (c.includes("amount") || c.includes("value") || c.includes("revenue") || c.includes("salary"))
    return parseFloat((Math.random() * 80000 + 20000).toFixed(2));
  if (c.includes("count") || c.includes("total") || c.includes("num"))
    return Math.floor(Math.random() * 500) + 50;
  if (c.includes("rate") || c.includes("pct") || c.includes("percent"))
    return parseFloat((Math.random() * 100).toFixed(1));
  return Math.floor(Math.random() * 200) + 10;
}

function generateDummyChartData(groupBy: string): any[] {
  return CHART_LABELS.map((label, i) => ({
    [groupBy]: label,
    value: parseFloat((Math.random() * 40000 + 5000).toFixed(2)),
    _colorClass: CHART_COLORS[i % CHART_COLORS.length],
  }));
}
// ────────────────────────────────────────────────────────────────────────────

export const ChartRenderer: React.FC<ChartRendererProps> = ({
  type,
  title,
  targetApiPath,
  props,
  refreshTrigger,
}) => {
  const [metricValue, setMetricValue] = useState<number | null>(null);
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [isOffline, setIsOffline] = useState(false);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      let query = `?operation=${props.operation}&column=${props.column}`;
      if (props.group_by) query += `&group_by=${props.group_by}`;
      if (props.table_name) query += `&table_name=${props.table_name}`;
      else if (props.target_table) query += `&table_name=${props.target_table}`;

      const response = await fetch(`${API_BASE_URL}${targetApiPath}${query}`);
      if (!response.ok) throw new Error(`status ${response.status}`);

      const json = await response.json();
      setIsOffline(false);

      if (props.group_by) {
        setChartData(json.data || generateDummyChartData(props.group_by));
      } else {
        const dataArr = json.data || [];
        setMetricValue(dataArr.length > 0 ? dataArr[0].value : generateDummyMetric(props.column));
      }
    } catch {
      // Backend unavailable → generate local demo data
      setIsOffline(true);
      if (props.group_by) {
        setChartData(generateDummyChartData(props.group_by));
      } else {
        setMetricValue(generateDummyMetric(props.column));
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [targetApiPath, refreshTrigger]);

  const renderIcon = (name: string) => {
    const IconComp = (Icons as any)[name.charAt(0).toUpperCase() + name.slice(1)] || Icons.Activity;
    return <IconComp className="w-5 h-5 text-teal-400" />;
  };

  const formatValue = (val: number | null) => {
    if (val === null) return "—";
    const col = props.column.toLowerCase();
    if (col.includes("amount") || col.includes("value") || col.includes("revenue") ||
        col.includes("price") || col.includes("salary"))
      return `$${val.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
    if (col.includes("rate") || col.includes("pct")) return `${val.toFixed(1)}%`;
    return val.toLocaleString();
  };

  // 1. METRIC CARD
  if (type === "MetricCard") {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 shadow-xl flex items-center justify-between transition-all hover:border-slate-300 relative">
        {isOffline && (
          <span className="absolute top-2 right-2 text-[9px] bg-amber-100 text-amber-600 px-1.5 py-0.5 rounded font-bold uppercase">Demo</span>
        )}
        <div>
          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">
            {props.label || title}
          </span>
          {loading ? (
            <div className="h-7 w-20 bg-slate-200 animate-pulse rounded-lg mt-1" />
          ) : (
            <h4 className="text-2xl font-bold font-mono text-slate-900">
              {formatValue(metricValue)}
            </h4>
          )}
        </div>
        <div className="p-3 bg-white rounded-xl border border-slate-200 flex items-center justify-center">
          {renderIcon(props.icon || "Activity")}
        </div>
      </div>
    );
  }

  // 2. BAR CHART
  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 shadow-xl flex flex-col justify-between min-h-[280px] relative">
      {isOffline && (
        <span className="absolute top-3 right-4 text-[9px] bg-amber-100 text-amber-600 px-1.5 py-0.5 rounded font-bold uppercase">Demo</span>
      )}

      <div className="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
        <h4 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <Icons.BarChart3 className="w-4 h-4 text-teal-400" />
          {title}
        </h4>
        <span className="text-[10px] bg-slate-100 text-teal-500 px-2 py-0.5 rounded font-mono uppercase font-semibold">
          {props.operation}
        </span>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs py-8">
          <Icons.Loader className="w-6 h-6 animate-spin text-teal-500 mb-1" />
          <span>Loading metrics...</span>
        </div>
      ) : chartData.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-400 text-xs py-8">
          <Icons.BarChart3 className="w-8 h-8 mb-2 opacity-30" />
          <span>No data available</span>
        </div>
      ) : (
        <div className="flex-1 flex items-end justify-around gap-2 h-44 pt-4 px-2">
          {chartData.map((row, idx) => {
            const label = row[props.group_by || ""] || `Cat ${idx + 1}`;
            const value = row.value || 0;
            const maxVal = Math.max(...chartData.map(r => r.value), 1);
            const heightPercent = Math.min(Math.max((value / maxVal) * 100, 8), 100);
            const colorClass = row._colorClass || CHART_COLORS[idx % CHART_COLORS.length];

            return (
              <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-5 bg-white text-[10px] text-teal-500 px-1.5 py-0.5 rounded border border-slate-200 z-10 font-bold font-mono whitespace-nowrap">
                  {formatValue(value)}
                </div>
                <div
                  style={{ height: `${heightPercent}%` }}
                  className={`w-full bg-gradient-to-t ${colorClass} rounded-t-lg transition-all duration-500 shadow-lg cursor-pointer hover:opacity-80`}
                />
                <span className="text-[10px] text-slate-500 block truncate w-full text-center mt-2 font-semibold">
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
