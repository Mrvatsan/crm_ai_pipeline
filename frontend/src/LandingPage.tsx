import React from "react";
import * as Icons from "lucide-react";

interface LandingPageProps {
  onStart: () => void;
}

// ── Static demo data for the hero mock UI ────────────────────────────────────
const MOCK_METRICS = [
  { label: "Total Revenue",  value: "$124,500", change: "+18%", icon: "TrendingUp",  color: "text-emerald-600", bg: "bg-emerald-50 border-emerald-200" },
  { label: "Active Clients", value: "3,842",    change: "+9%",  icon: "Users",       color: "text-blue-600",    bg: "bg-blue-50 border-blue-200" },
  { label: "Open Deals",     value: "267",       change: "+5%",  icon: "Briefcase",   color: "text-violet-600",  bg: "bg-violet-50 border-violet-200" },
];

const MOCK_BARS = [
  { label: "Jan", height: 45,  color: "bg-gradient-to-t from-emerald-500 to-teal-400" },
  { label: "Feb", height: 68,  color: "bg-gradient-to-t from-emerald-500 to-teal-400" },
  { label: "Mar", height: 52,  color: "bg-gradient-to-t from-emerald-500 to-teal-400" },
  { label: "Apr", height: 90,  color: "bg-gradient-to-t from-emerald-600 to-emerald-400" },
  { label: "May", height: 75,  color: "bg-gradient-to-t from-emerald-500 to-teal-400" },
  { label: "Jun", height: 100, color: "bg-gradient-to-t from-teal-500 to-emerald-400" },
];

const MOCK_ROWS = [
  { name: "Acme Corp",      status: "Active",   value: "$24,500", stage: "Closed Won" },
  { name: "Nova Systems",   status: "Pending",  value: "$18,200", stage: "Proposal" },
  { name: "TechStream Inc", status: "Active",   value: "$31,000", stage: "Negotiation" },
  { name: "Orbit Ventures", status: "Review",   value: "$9,800",  stage: "Discovery" },
];

const MOCK_NAV = [
  { label: "Dashboard",  icon: "LayoutDashboard", active: true },
  { label: "Clients",    icon: "Users",           active: false },
  { label: "Deals",      icon: "Briefcase",       active: false },
  { label: "Reports",    icon: "BarChart3",       active: false },
  { label: "Settings",   icon: "Settings",        active: false },
];

const STATUS_COLORS: Record<string, string> = {
  Active:  "bg-emerald-100 text-emerald-700",
  Pending: "bg-amber-100 text-amber-700",
  Review:  "bg-blue-100 text-blue-700",
};
// ─────────────────────────────────────────────────────────────────────────────

export const LandingPage: React.FC<LandingPageProps> = ({ onStart }) => {
  return (
    <div className="min-h-screen bg-[#F0FDF4] text-slate-800 font-sans selection:bg-emerald-500/20 antialiased flex flex-col">

      {/* 1. Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-emerald-100 px-8 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-50 border border-emerald-200 rounded-xl">
            <Icons.Sparkles className="w-5 h-5 text-emerald-600" />
          </div>
          <span className="text-sm font-black tracking-widest text-slate-900 uppercase">
            AI Software Compiler
          </span>
        </div>
        <button
          onClick={onStart}
          className="bg-white border border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800 px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm flex items-center gap-2"
        >
          Open App <Icons.ArrowRight className="w-3.5 h-3.5" />
        </button>
      </header>

      {/* 2. Hero Section */}
      <main className="flex-1 flex flex-col items-center pt-20 pb-20 px-6 relative overflow-hidden">

        {/* Background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-emerald-300/20 blur-[120px] rounded-full pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-emerald-200 text-emerald-700 text-xs font-bold mb-8 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          v2.2 Compiler Engine is Live
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 text-center max-w-4xl leading-tight mb-6">
          Build software at the <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500">
            speed of thought
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-600 text-center max-w-2xl font-medium leading-relaxed mb-10">
          Instantly generate fully-functional databases, REST APIs, and live interfaces using just plain English. Zero coding required.
        </p>

        <button
          onClick={onStart}
          className="bg-[#10B981] hover:bg-[#059669] text-white text-lg font-black px-10 py-5 rounded-full shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/40 transition-all hover:-translate-y-1 flex items-center gap-3 border border-[#059669]"
        >
          Start Building Now
          <Icons.Zap className="w-5 h-5 fill-white" />
        </button>

        {/* ── Rich Mock App Preview ─────────────────────────────────── */}
        <div className="w-full max-w-5xl mt-16 bg-white border border-slate-200 rounded-3xl shadow-2xl shadow-emerald-900/10 overflow-hidden relative z-10">

          {/* Browser chrome bar */}
          <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center gap-3">
            <div className="flex gap-1.5">
              <span className="w-3 h-3 rounded-full bg-red-400" />
              <span className="w-3 h-3 rounded-full bg-amber-400" />
              <span className="w-3 h-3 rounded-full bg-emerald-400" />
            </div>
            <div className="flex-1 flex justify-center">
              <div className="bg-white border border-slate-200 rounded-lg px-4 py-1 text-[11px] text-slate-500 font-mono flex items-center gap-2 w-64">
                <Icons.Lock className="w-3 h-3 text-emerald-500" />
                ai-compiler-app.vercel.app
              </div>
            </div>
          </div>

          {/* App content */}
          <div className="flex h-[460px]">

            {/* Sidebar */}
            <div className="w-52 bg-slate-50 border-r border-slate-200 flex flex-col p-3 shrink-0">
              <div className="px-3 py-3 mb-2">
                <div className="flex items-center gap-2">
                  <Icons.Cpu className="w-4 h-4 text-emerald-500 animate-pulse" />
                  <span className="text-xs font-extrabold text-emerald-600 tracking-wide">CRM Dashboard</span>
                </div>
                <span className="text-[9px] text-slate-400 font-semibold uppercase tracking-widest">Live Runtime</span>
              </div>

              {/* Role badge */}
              <div className="mx-2 mb-3 bg-white border border-slate-200 rounded-xl px-3 py-2">
                <div className="flex items-center gap-1.5 mb-1">
                  <Icons.ShieldCheck className="w-3 h-3 text-emerald-500" />
                  <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider">Role</span>
                </div>
                <span className="text-xs font-black text-emerald-700 uppercase tracking-wide">Admin</span>
              </div>

              {/* Nav items */}
              <div className="space-y-0.5 px-1">
                {MOCK_NAV.map((item) => {
                  const Icon = (Icons as any)[item.icon] || Icons.Circle;
                  return (
                    <div
                      key={item.label}
                      className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-semibold ${
                        item.active
                          ? "bg-emerald-50 text-emerald-700 border-l-2 border-emerald-500"
                          : "text-slate-500"
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5 shrink-0" />
                      {item.label}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Main content */}
            <div className="flex-1 overflow-hidden flex flex-col bg-white">

              {/* Top bar */}
              <div className="border-b border-slate-100 px-6 py-3 flex items-center justify-between shrink-0">
                <div>
                  <h2 className="text-sm font-extrabold text-slate-800">Dashboard Overview</h2>
                  <p className="text-[10px] text-slate-400 font-medium">AI-generated · 3 tables · 5 API routes</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 bg-emerald-50 border border-emerald-200 rounded-lg px-2.5 py-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] font-bold text-emerald-700">Live</span>
                  </div>
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                    <Icons.User className="w-3.5 h-3.5 text-white" />
                  </div>
                </div>
              </div>

              {/* Scrollable body */}
              <div className="flex-1 overflow-auto p-5 space-y-5">

                {/* Metric cards */}
                <div className="grid grid-cols-3 gap-4">
                  {MOCK_METRICS.map((m) => {
                    const Icon = (Icons as any)[m.icon] || Icons.Activity;
                    return (
                      <div key={m.label} className={`bg-white border ${m.bg} rounded-2xl p-4 shadow-sm`}>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{m.label}</span>
                          <Icon className={`w-4 h-4 ${m.color}`} />
                        </div>
                        <div className="text-xl font-black text-slate-900">{m.value}</div>
                        <div className="text-[10px] font-bold text-emerald-600 mt-1">{m.change} this month</div>
                      </div>
                    );
                  })}
                </div>

                {/* Chart + Table row */}
                <div className="grid grid-cols-5 gap-4">

                  {/* Bar Chart */}
                  <div className="col-span-2 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <Icons.BarChart3 className="w-3.5 h-3.5 text-teal-500" />
                        Revenue · 2024
                      </span>
                      <span className="text-[9px] bg-teal-50 text-teal-600 px-2 py-0.5 rounded font-bold uppercase">SUM</span>
                    </div>
                    <div className="flex items-end gap-2 h-28 pt-2">
                      {MOCK_BARS.map((bar) => (
                        <div key={bar.label} className="flex-1 flex flex-col items-center justify-end h-full">
                          <div
                            style={{ height: `${bar.height}%` }}
                            className={`w-full ${bar.color} rounded-t-md shadow-sm`}
                          />
                          <span className="text-[9px] text-slate-400 font-bold mt-1">{bar.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Data table */}
                  <div className="col-span-3 bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
                    <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                        <Icons.Database className="w-3.5 h-3.5 text-teal-500" />
                        clients
                      </span>
                      <span className="text-[9px] text-slate-400 font-semibold">{MOCK_ROWS.length} records</span>
                    </div>
                    <table className="w-full text-[10px]">
                      <thead>
                        <tr className="bg-slate-50 border-b border-slate-100 text-slate-500 font-bold uppercase tracking-widest">
                          <th className="px-4 py-2 text-left">Name</th>
                          <th className="px-3 py-2 text-left">Status</th>
                          <th className="px-3 py-2 text-left">Value</th>
                          <th className="px-3 py-2 text-left">Stage</th>
                        </tr>
                      </thead>
                      <tbody>
                        {MOCK_ROWS.map((row, i) => (
                          <tr key={i} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                            <td className="px-4 py-2.5 font-semibold text-slate-800">{row.name}</td>
                            <td className="px-3 py-2.5">
                              <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold ${STATUS_COLORS[row.status] || "bg-slate-100 text-slate-600"}`}>
                                {row.status}
                              </span>
                            </td>
                            <td className="px-3 py-2.5 font-mono font-semibold text-teal-600">{row.value}</td>
                            <td className="px-3 py-2.5 text-slate-500">{row.stage}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            </div>
          </div>

          {/* Bottom fade overlay */}
          <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-white/80 to-transparent pointer-events-none rounded-b-3xl" />
        </div>
        {/* ─────────────────────────────────────────────────────────── */}

      </main>

      {/* 3. Features Grid */}
      <section id="features" className="bg-white border-t border-slate-200 py-24 px-6 relative z-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-4">Everything you need to ship faster</h2>
            <p className="text-slate-500 font-medium">The AI compiler handles the heavy lifting so you can focus on the product.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-white rounded-2xl border border-emerald-200 flex items-center justify-center mb-6 shadow-sm">
                <Icons.BrainCircuit className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Natural Language AI</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Describe your idea in plain English. Our advanced LLM interprets your requirements and architects the entire application structure instantly.
              </p>
            </div>

            <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-white rounded-2xl border border-emerald-200 flex items-center justify-center mb-6 shadow-sm">
                <Icons.Zap className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Live Compilation</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Watch your application compile in real-time. The interface patches itself dynamically as the AI builds databases, APIs, and UI components.
              </p>
            </div>

            <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-white rounded-2xl border border-emerald-200 flex items-center justify-center mb-6 shadow-sm">
                <Icons.Database className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Full-Stack Generation</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                We don't just generate UI mockups. The compiler builds functional relational databases, REST APIs, and Role-Based Access Control logic.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-slate-200 py-12 text-center text-slate-500 text-sm font-medium">
        <p>&copy; {new Date().getFullYear()} AI Software Compiler. All rights reserved.</p>
      </footer>
    </div>
  );
};
