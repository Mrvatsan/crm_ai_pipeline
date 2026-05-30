import { useState } from "react";
import * as Icons from "lucide-react";
import { NavRenderer } from "../components/NavRenderer";
import { TableRenderer } from "../components/TableRenderer";
import { FormRenderer } from "../components/FormRenderer";
import { ChartRenderer } from "../components/ChartRenderer";
import { PremiumGate } from "../components/PremiumGate";

interface SchemaInterpreterProps {
  spec: any; // AppSpecification AST JSON
  activeRole: string;
  setActiveRole: (role: string) => void;
}

export const SchemaInterpreter: React.FC<SchemaInterpreterProps> = ({
  spec,
  activeRole,
  setActiveRole,
}) => {
  const [activeRoute, setActiveRoute] = useState("/");
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  if (!spec || !spec.ui_schema) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-white border border-slate-200 rounded-3xl p-12 text-slate-500 min-h-[400px]">
        <span>No dynamic application is running. Execute the AI Compiler to boot a schema runtime.</span>
      </div>
    );
  }

  const { nav_items, pages } = spec.ui_schema;
  const roles = spec.auth_schema?.roles?.map((r: any) => r.role_name) || ["admin", "user"];

  // Find current active page spec
  const currentPage = pages.find((p: any) => p.route === activeRoute) || pages[0];

  const handleDataRefresh = () => {
    // Increment trigger to force dynamic tables & metrics to re-query database
    setRefreshTrigger((prev) => prev + 1);
  };

  // Determine if active route is gated for the current simulated role
  const isRoleGated =
    currentPage.required_role &&
    currentPage.required_role !== activeRole &&
    activeRole !== "admin";

  const renderComponent = (comp: any) => {
    const key = `${comp.id}_${refreshTrigger}`;

    switch (comp.type) {
      case "Header":
        return (
          <div key={key} className="col-span-12 mb-6 border-b border-slate-200 pb-3">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-600 bg-clip-text text-transparent">
              {comp.title}
            </h2>
            {comp.props?.subtitle && <p className="text-sm text-slate-500 mt-1">{comp.props.subtitle}</p>}
          </div>
        );

      case "MetricCard":
        return (
          <div key={key} style={{ gridColumn: `span ${comp.grid_span || 12} / span 12` }}>
            <ChartRenderer
              id={comp.id}
              type="MetricCard"
              title={comp.title}
              targetApiPath={comp.target_api_path}
              props={comp.props}
              refreshTrigger={refreshTrigger}
            />
          </div>
        );

      case "Chart":
        return (
          <div key={key} style={{ gridColumn: `span ${comp.grid_span || 12} / span 12` }}>
            <ChartRenderer
              id={comp.id}
              type="Chart"
              title={comp.title}
              targetApiPath={comp.target_api_path}
              props={comp.props}
              refreshTrigger={refreshTrigger}
            />
          </div>
        );

      case "Table":
        return (
          <div key={key} className="col-span-12">
            <TableRenderer
              title={comp.title}
              tableName={comp.props?.table_name || "dynamic_table"}
              targetApiPath={comp.target_api_path}
              columns={comp.props?.columns || []}
              actions={comp.props?.actions || []}
              activeRole={activeRole}
              refreshTrigger={refreshTrigger}
              onRefresh={handleDataRefresh}
            />
          </div>
        );

      case "Form":
        return (
          <div key={key} className="col-span-12">
            <FormRenderer
              title={comp.title}
              targetApiPath={comp.target_api_path}
              fields={comp.props?.fields || []}
              onSuccess={handleDataRefresh}
              activeRole={activeRole}
            />
          </div>
        );

      case "PremiumGate":
        return (
          <div key={key} className="col-span-12">
            <PremiumGate
              title={comp.title}
              upgradeMessage={comp.props?.upgrade_message}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex bg-white border border-slate-200 rounded-3xl overflow-hidden shadow-lg shadow-emerald-900/5 min-h-[550px] relative">
      {/* 1. Left Dynamic Nav sidebar */}
      <NavRenderer
        appName={spec.app_name}
        navItems={nav_items}
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        activeRole={activeRole}
        setActiveRole={setActiveRole}
        availableRoles={roles}
      />

      {/* 2. Main Page Render viewport */}
      <div className="flex-1 p-8 overflow-y-auto max-h-[700px]">
        {isRoleGated ? (
          /* Role Gate Block Overlay */
          <div className="py-20 flex flex-col items-center justify-center text-center max-w-md mx-auto gap-4">
            <div className="p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center justify-center">
              <Icons.ShieldAlert className="w-8 h-8 text-red-500" />
            </div>
            <h3 className="text-lg font-bold text-red-600">Role Access Restricted</h3>
            <p className="text-xs text-slate-500 leading-relaxed">
              This page requires a higher permission tier. Switch your active role simulation inside the sidebar to bypass this gate.
            </p>
          </div>
        ) : currentPage.is_premium_gated ? (
          /* Premium upgrade lock gate */
          <PremiumGate
            title={currentPage.title}
            upgradeMessage={spec.auth_schema?.premium_gating?.upgrade_message}
          />
        ) : (
          /* Page Components Grid Container */
          <div className="grid grid-cols-12 gap-6">
            {currentPage.components?.map((comp: any) => renderComponent(comp))}
          </div>
        )}
      </div>
    </div>
  );
};
