import React from "react";
import * as Icons from "lucide-react";

interface NavItem {
  label: string;
  route: string;
  icon: string;
  required_role?: string | null;
}

interface NavRendererProps {
  navItems: NavItem[];
  activeRoute: string;
  setActiveRoute: (route: string) => void;
  activeRole: string;
  setActiveRole: (role: string) => void;
  availableRoles: string[];
}

export const NavRenderer: React.FC<NavRendererProps> = ({
  navItems,
  activeRoute,
  setActiveRoute,
  activeRole,
  setActiveRole,
  availableRoles,
}) => {
  // Dynamically resolve icon names from Lucide React package
  const renderIcon = (iconName: string) => {
    const IconComponent = (Icons as any)[iconName.charAt(0).toUpperCase() + iconName.slice(1)] || Icons.HelpCircle;
    return <IconComponent className="w-5 h-5" />;
  };

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col h-full">
      {/* 1. Header with System Meta */}
      <div className="p-6 border-b border-slate-800">
        <h2 className="text-xl font-bold bg-gradient-to-r from-teal-400 to-indigo-400 bg-clip-text text-transparent flex items-center gap-2">
          <Icons.Cpu className="w-6 h-6 text-teal-400 animate-pulse" />
          Runtime App
        </h2>
        <p className="text-xs text-slate-500 mt-1 uppercase font-semibold tracking-wider">Executable Runtime</p>
      </div>

      {/* 2. Interactive Role Switcher Selector */}
      <div className="p-4 mx-4 my-3 bg-slate-950 rounded-xl border border-slate-800">
        <label className="text-xs text-slate-500 uppercase tracking-widest font-bold block mb-2 flex items-center gap-1.5">
          <Icons.ShieldAlert className="w-3.5 h-3.5 text-teal-500" />
          Simulate Active Role
        </label>
        <select
          value={activeRole}
          onChange={(e) => setActiveRole(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-2.5 py-1.5 focus:ring-1 focus:ring-teal-500 focus:outline-none"
        >
          {availableRoles.map((role) => (
            <option key={role} value={role}>
              {role.charAt(0).toUpperCase() + role.slice(1)}
            </option>
          ))}
        </select>
        <span className="text-[10px] text-slate-600 block mt-1.5 italic">RBAC policies are dynamically applied</span>
      </div>

      {/* 3. Navigation items lists */}
      <div className="flex-1 px-3 py-4 space-y-1">
        <label className="text-[10px] text-slate-500 uppercase tracking-widest font-bold px-3 block mb-2">Main Navigation</label>
        {navItems.map((item, index) => {
          const isGated = !!(item.required_role && item.required_role !== activeRole && activeRole !== "admin");
          const isActive = activeRoute === item.route;

          return (
            <button
              key={index}
              onClick={() => {
                if (!isGated) setActiveRoute(item.route);
              }}
              disabled={isGated}
              className={`w-full text-left flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                isGated
                  ? "opacity-40 cursor-not-allowed text-slate-600 hover:bg-transparent"
                  : isActive
                  ? "bg-teal-500/10 text-teal-400 border-l-2 border-teal-500 font-semibold"
                  : "hover:bg-slate-800/50 text-slate-400 hover:text-slate-200"
              }`}
            >
              <div className="flex items-center gap-3">
                {renderIcon(item.icon)}
                <span>{item.label}</span>
              </div>
              
              {/* Gate Indicators */}
              {item.required_role && (
                <div className="flex items-center">
                  {isGated ? (
                    <Icons.Lock className="w-3.5 h-3.5 text-slate-600" />
                  ) : (
                    <span className="text-[9px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded uppercase font-bold">
                      {item.required_role}
                    </span>
                  )}
                </div>
              )}
            </button>
          );
        })}
      </div>
      
      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 text-center text-xs text-slate-600">
        Active Schema Version 1.0.0
      </div>
    </div>
  );
};
