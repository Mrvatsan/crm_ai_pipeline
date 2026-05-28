import React from "react";
import * as Icons from "lucide-react";

interface PremiumGateProps {
  title: string;
  upgradeMessage?: string;
  onUpgrade?: () => void;
}

export const PremiumGate: React.FC<PremiumGateProps> = ({
  title,
  upgradeMessage = "This premium page is locked. Upgrade to the Enterprise Subscription tier to unlock advanced intelligence metrics.",
  onUpgrade,
}) => {
  return (
    <div className="relative border border-slate-800 rounded-3xl bg-slate-900/60 overflow-hidden min-h-[350px] flex items-center justify-center p-8 text-center shadow-2xl">
      {/* 1. Blurred Background Elements for Premium Glassmorphism Look */}
      <div className="absolute inset-0 bg-slate-950/45 backdrop-blur-md z-0" />
      <div className="absolute -top-16 -left-16 w-48 h-48 bg-teal-500/10 rounded-full blur-3xl" />
      <div className="absolute -bottom-16 -right-16 w-48 h-48 bg-indigo-500/10 rounded-full blur-3xl" />

      {/* 2. Interactive Overlay Container */}
      <div className="relative z-10 max-w-md flex flex-col items-center gap-4">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-3xl shadow-xl shadow-teal-500/5 flex items-center justify-center relative">
          <Icons.Gem className="w-10 h-10 text-teal-400 animate-bounce" />
          <div className="absolute -inset-0.5 bg-gradient-to-r from-teal-500 to-indigo-500 rounded-3xl opacity-25 blur" />
        </div>

        <h3 className="text-xl font-bold bg-gradient-to-r from-teal-300 to-indigo-300 bg-clip-text text-transparent mt-2">
          {title}
        </h3>
        
        <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
          {upgradeMessage}
        </p>

        <div className="flex flex-col sm:flex-row gap-3 mt-4 w-full justify-center">
          <button
            onClick={() => {
              if (onUpgrade) onUpgrade();
              else alert("Billing Demo: Standard pricing checkout tier compiled successfully.");
            }}
            className="bg-gradient-to-r from-teal-500 to-indigo-500 text-slate-900 font-bold text-xs px-5 py-3 rounded-2xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-1.5 shadow-lg shadow-teal-500/20"
          >
            <Icons.CreditCard className="w-4 h-4" />
            Unlock Premium Tier
          </button>
          
          <button
            onClick={() => alert("Monetization telemetry has been logged for evaluation checks.")}
            className="bg-slate-950 border border-slate-800 text-slate-400 text-xs px-4 py-3 rounded-2xl hover:bg-slate-900 transition-colors"
          >
            View Pricing Plans
          </button>
        </div>

        <span className="text-[10px] text-slate-600 block mt-2 flex items-center gap-1">
          <Icons.ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
          Secure checkout integrated with Dynamic Billing Auth
        </span>
      </div>
    </div>
  );
};
