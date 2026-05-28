import React, { useState, useEffect } from "react";
import * as Icons from "lucide-react";

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
  };
  refreshTrigger: number;
}

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
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      // Build dynamic aggregation path:
      // http://localhost:8000/api/runtime/analytics/metrics?operation=X&column=Y&group_by=Z
      let query = `?operation=${props.operation}&column=${props.column}`;
      if (props.group_by) {
        query += `&group_by=${props.group_by}`;
      }

      const response = await fetch(`http://localhost:8000${targetApiPath}${query}`);
      if (!response.ok) {
        throw new Error(`Analytics failed with status ${response.status}`);
      }
      const json = await response.json();
      
      if (props.group_by) {
        // Formats for Chart
        setChartData(json.data || []);
      } else {
        // Formats for MetricCard
        const dataArr = json.data || [];
        const finalVal = dataArr.length > 0 ? dataArr[0].value : 0;
        setMetricValue(finalVal);
      }
    } catch (err: any) {
      setError(err.message);
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

  // 1. RENDER SINGLE METRIC INDICATOR CARD
  if (type === "MetricCard") {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl flex items-center justify-between transition-all hover:border-slate-700">
        <div>
          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">
            {props.label || title}
          </span>
          {loading ? (
            <div className="h-7 w-20 bg-slate-850 animate-pulse rounded-lg mt-1" />
          ) : error ? (
            <span className="text-red-400 font-semibold text-xs block mt-1">Error Loading</span>
          ) : (
            <h4 className="text-2xl font-bold font-mono text-slate-100">
              {props.column.includes("value") || props.column.includes("amount") ? (
                `$${(metricValue || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}`
              ) : (
                (metricValue || 0).toLocaleString()
              )}
            </h4>
          )}
        </div>
        <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center">
          {renderIcon(props.icon || "Activity")}
        </div>
      </div>
    );
  }

  // 2. RENDER GORGEOUS RESPONSIVE BAR CHART GRAPH
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between min-h-[280px]">
      {/* Chart Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <h4 className="text-sm font-bold text-slate-200 flex items-center gap-2">
          <Icons.BarChart3 className="w-4 h-4 text-teal-400" />
          {title}
        </h4>
        <span className="text-[10px] bg-slate-800 text-teal-400 px-2 py-0.5 rounded font-mono uppercase font-semibold">
          Aggregation: {props.operation}
        </span>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-600 text-xs py-8">
          <Icons.Loader className="w-6 h-6 animate-spin text-teal-500 mb-1" />
          <span>Compiling Metrics...</span>
        </div>
      ) : error ? (
        <div className="flex-1 flex flex-col items-center justify-center text-red-400 text-xs py-8 gap-1.5 text-center">
          <Icons.ShieldAlert className="w-6 h-6 text-red-500" />
          <span>Analytics Offline</span>
        </div>
      ) : chartData.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-slate-600 text-xs py-8">
          <Icons.Inbox className="w-8 h-8 text-slate-800 mb-1" />
          <span>Empty Seed Metrics</span>
        </div>
      ) : (
        /* Visual CSS Graph Primitives */
        <div className="flex-1 flex items-end justify-around gap-2 h-44 pt-4 px-2">
          {chartData.map((row, idx) => {
            const label = row[props.group_by || ""] || `Category ${idx}`;
            const value = row.value || 0;
            
            // Calculate height percentage based on max value in dataset
            const maxVal = Math.max(...chartData.map((r) => r.value), 1);
            const heightPercent = Math.min(Math.max((value / maxVal) * 100, 10), 100);

            return (
              <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                {/* Value Hover tooltip */}
                <div className="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-5 bg-slate-950 text-[10px] text-teal-400 px-1.5 py-0.5 rounded border border-slate-800 z-10 font-bold font-mono">
                  {props.column.includes("value") || props.column.includes("amount") ? `$${value.toLocaleString()}` : value}
                </div>
                
                {/* Visual bar block */}
                <div
                  style={{ height: `${heightPercent}%` }}
                  className="w-full bg-gradient-to-t from-teal-500 to-indigo-500 rounded-t-lg transition-all duration-500 hover:from-teal-400 hover:to-indigo-400 shadow-lg shadow-teal-500/10 cursor-pointer"
                />

                {/* X Axis Label */}
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
