import React from "react";
import * as Icons from "lucide-react";

interface LandingPageProps {
  onStart: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStart }) => {
  return (
    <div className="min-h-screen bg-[#F0FDF4] text-slate-800 font-sans selection:bg-emerald-500/20 antialiased flex flex-col">
      {/* 1. Header Navigation */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-emerald-100 px-8 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-emerald-50 border border-emerald-200 rounded-xl">
            <Icons.Sparkles className="w-5 h-5 text-emerald-600" />
          </div>
          <span className="text-sm font-black tracking-widest text-slate-900 uppercase">
            AI Software Compiler
          </span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-bold text-slate-500">
          <a href="#features" className="hover:text-emerald-600 transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-emerald-600 transition-colors">How it Works</a>
          <a href="#pricing" className="hover:text-emerald-600 transition-colors">Pricing</a>
        </nav>
        <button
          onClick={onStart}
          className="bg-white border border-emerald-200 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800 px-5 py-2.5 rounded-full text-xs font-bold transition-all shadow-sm flex items-center gap-2"
        >
          Open App <Icons.ArrowRight className="w-3.5 h-3.5" />
        </button>
      </header>

      {/* 2. Hero Section */}
      <main className="flex-1 flex flex-col items-center pt-24 pb-20 px-6 relative overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-300/20 blur-[100px] rounded-full pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-emerald-200 text-emerald-700 text-xs font-bold mb-8 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          v2.2 Compiler Engine is Live
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 text-center max-w-4xl leading-tight mb-8">
          Build software at the <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-500">
            speed of thought
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-600 text-center max-w-2xl font-medium leading-relaxed mb-12">
          Instantly generate fully-functional databases, REST APIs, and live interfaces using just plain English. Zero coding required.
        </p>

        <button
          onClick={onStart}
          className="bg-[#10B981] hover:bg-[#059669] text-white text-lg font-black px-10 py-5 rounded-full shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/40 transition-all hover:-translate-y-1 flex items-center gap-3 border border-[#059669]"
        >
          Start Building Now
          <Icons.Zap className="w-5 h-5 fill-white" />
        </button>

        {/* Mock Terminal/Interface Preview */}
        <div className="w-full max-w-5xl mt-20 bg-white border border-slate-200 rounded-3xl shadow-2xl p-2 relative z-10 transform perspective-[1000px] rotateX-[5deg]">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#F0FDF4] opacity-50 rounded-3xl pointer-events-none" />
          <div className="bg-slate-50 rounded-2xl border border-slate-100 overflow-hidden h-[400px] flex">
            {/* Mock Sidebar */}
            <div className="w-48 bg-white border-r border-slate-200 p-4 hidden md:flex flex-col gap-3 opacity-70">
              <div className="h-4 w-24 bg-emerald-100 rounded-full mb-4" />
              <div className="h-8 w-full bg-slate-100 rounded-lg" />
              <div className="h-8 w-full bg-emerald-50 rounded-lg" />
              <div className="h-8 w-full bg-slate-100 rounded-lg" />
            </div>
            {/* Mock Content */}
            <div className="flex-1 p-8 opacity-70 flex flex-col gap-6">
              <div className="h-8 w-48 bg-slate-200 rounded-lg" />
              <div className="grid grid-cols-3 gap-4">
                <div className="h-24 bg-white border border-slate-200 rounded-xl shadow-sm" />
                <div className="h-24 bg-white border border-slate-200 rounded-xl shadow-sm" />
                <div className="h-24 bg-emerald-50 border border-emerald-100 rounded-xl shadow-sm" />
              </div>
              <div className="h-48 bg-white border border-slate-200 rounded-xl shadow-sm w-full" />
            </div>
          </div>
        </div>
      </main>

      {/* 3. Features Grid */}
      <section id="features" className="bg-white border-t border-slate-200 py-24 px-6 relative z-20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-4">Everything you need to ship faster</h2>
            <p className="text-slate-500 font-medium">The AI compiler handles the heavy lifting so you can focus on the product.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-white rounded-2xl border border-emerald-200 flex items-center justify-center mb-6 shadow-sm">
                <Icons.BrainCircuit className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Natural Language AI</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Describe your idea in plain English. Our advanced LLM interprets your requirements and architects the entire application structure instantly.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-white rounded-2xl border border-emerald-200 flex items-center justify-center mb-6 shadow-sm">
                <Icons.Zap className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-3">Live Compilation</h3>
              <p className="text-sm text-slate-600 leading-relaxed font-medium">
                Watch your application compile in real-time. The interface patches itself dynamically as the AI builds databases, APIs, and UI components.
              </p>
            </div>

            {/* Feature 3 */}
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
