import React, { useState } from "react";
import * as Icons from "lucide-react";

interface FormField {
  name: string;
  label: string;
  type: "text" | "number" | "email" | "select" | "date" | "textarea";
  required?: boolean;
  options?: string[];
  placeholder?: string;
}

interface FormRendererProps {
  title: string;
  targetApiPath: string;
  fields: FormField[];
  onSuccess: () => void;
  activeRole: string;
}

export const FormRenderer: React.FC<FormRendererProps> = ({
  title,
  targetApiPath,
  fields,
  onSuccess,
  activeRole,
}) => {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const canWrite = activeRole === "admin" || activeRole === "sales_rep" || activeRole === "developer" || activeRole === "manager";

  const handleChange = (name: string, value: any) => {
    setFormData((prev: Record<string, any>) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canWrite) {
      setError("RBAC Permission Denied: Your simulated role does not have write scopes.");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMsg(null);

    // Convert values if types are numeric
    const parsedData: Record<string, any> = {};
    fields.forEach((field) => {
      const val = formData[field.name];
      if (field.type === "number") {
        parsedData[field.name] = val !== undefined && val !== "" ? parseFloat(val) : 0;
      } else {
        parsedData[field.name] = val;
      }
    });

    try {
      const response = await fetch(`http://localhost:8000${targetApiPath}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsedData),
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      setSuccessMsg("Record added successfully!");
      setFormData({});
      onSuccess(); // Trigger table refresh!
      
      // Auto-clear success message
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(`Failed to create record: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-200 pb-3">
        <Icons.PlusSquare className="w-5 h-5 text-teal-400" />
        <h3 className="text-lg font-bold text-slate-800">{title}</h3>
      </div>

      {!canWrite && (
        <div className="mb-4 p-3 bg-red-950/30 border border-red-900/50 text-red-400 rounded-xl text-xs flex items-center gap-2">
          <Icons.ShieldAlert className="w-4 h-4" />
          <span>Form is read-only. Your current simulated role cannot create records.</span>
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-950/20 border border-red-900/30 text-red-400 rounded-xl text-xs flex items-center gap-2">
          <Icons.AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="mb-4 p-3 bg-teal-950/30 border border-teal-900/50 text-teal-400 rounded-xl text-xs flex items-center gap-2">
          <Icons.CheckCircle className="w-4 h-4" />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {fields.map((field) => (
            <div key={field.name} className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-slate-500 tracking-wide uppercase flex items-center gap-1">
                {field.label}
                {field.required && <span className="text-teal-400">*</span>}
              </label>

              {field.type === "select" ? (
                <select
                  disabled={!canWrite}
                  required={field.required}
                  value={formData[field.name] || ""}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 focus:ring-1 focus:ring-teal-500 focus:outline-none disabled:opacity-50"
                >
                  <option value="">Select option...</option>
                  {field.options?.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : field.type === "textarea" ? (
                <textarea
                  disabled={!canWrite}
                  required={field.required}
                  placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}...`}
                  value={formData[field.name] || ""}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 focus:ring-1 focus:ring-teal-500 focus:outline-none min-h-[80px] disabled:opacity-50 md:col-span-2"
                />
              ) : (
                <input
                  disabled={!canWrite}
                  type={field.type}
                  required={field.required}
                  placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}...`}
                  value={formData[field.name] || ""}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-sm text-slate-800 focus:ring-1 focus:ring-teal-500 focus:outline-none disabled:opacity-50"
                />
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end pt-3 border-t border-slate-200">
          <button
            type="submit"
            disabled={loading || !canWrite}
            className="bg-gradient-to-r from-teal-500 to-emerald-500 text-slate-900 font-bold px-5 py-2.5 rounded-xl text-sm transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:scale-100 flex items-center gap-1.5 shadow-lg shadow-teal-500/10"
          >
            {loading ? (
              <Icons.Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Icons.Save className="w-4 h-4" />
            )}
            Save Record
          </button>
        </div>
      </form>
    </div>
  );
};
