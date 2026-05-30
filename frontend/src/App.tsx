import { useState, useEffect, useRef } from "react";
import * as Icons from "lucide-react";
import { SchemaInterpreter } from "./runtime/SchemaInterpreter";
import { LandingPage } from "./LandingPage";

interface PipelineStage {
  name: string;
  status: "idle" | "running" | "success" | "healed" | "failed";
  latency: number; // ms
  details: string;
}

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
  timestamp: string;
  status?: "compiling" | "completed" | "failed";
  stages?: PipelineStage[];
  latency?: number;
  tablesCount?: number;
  repairsCount?: number;
  errors?: string[];
  repairs?: string[];
  spec?: any;
}

interface ProjectHistory {
  id: string;
  prompt: string;
  appName: string;
  timestamp: string;
  spec: any;
}

export default function App() {
  const [hasStarted, setHasStarted] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [activeTab, setActiveTab] = useState<"preview" | "schema">("preview");
  const [activeSchemaTab, setActiveSchemaTab] = useState<"ui" | "api" | "db" | "auth">("ui");
  const [activeRole, setActiveRole] = useState("admin");

  // Configuration settings (stored in browser localstorage)
  const [apiKey, setApiKey] = useState(() => localStorage.getItem("gemini_api_key") || "");
  const [geminiModel, setGeminiModel] = useState(() => localStorage.getItem("gemini_model") || "gemini-2.5-flash");
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    localStorage.setItem("gemini_api_key", apiKey);
  }, [apiKey]);

  useEffect(() => {
    localStorage.setItem("gemini_model", geminiModel);
  }, [geminiModel]);

  // Conversational message threads state
  const [messages, setMessages] = useState<Message[]>([]);
  
  // Generation history & previous apps state
  const [projects, setProjects] = useState<ProjectHistory[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

  // Active compiled application spec state
  const [compiledSpec, setCompiledSpec] = useState<any>(null);
  
  // Compilation loading state
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<"chat" | "loading" | "preview">("chat");
  const [loadingMessage, setLoadingMessage] = useState("");
  const [displayMessage, setDisplayMessage] = useState("");
  const [fade, setFade] = useState(false);

  // Smooth cinematic text transition
  useEffect(() => {
    if (!loadingMessage) return;
    setFade(false); // Fade out old text
    const timeout = setTimeout(() => {
      setDisplayMessage(loadingMessage);
      setFade(true); // Fade in new text
    }, 700); // 700ms gap for fade out
    return () => clearTimeout(timeout);
  }, [loadingMessage]);

  // Auto-growing textarea & scrolling refs
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Adjust prompt textarea height automatically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [prompt]);

  // Scroll chat thread to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const selectExample = (text: string) => {
    setPrompt(text);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleStartNewProject = () => {
    setPrompt("");
    setCompiledSpec(null);
    setMessages([]);
    setSelectedProjectId(null);
    setViewMode("chat");
  };

  const loadPastProject = (proj: ProjectHistory) => {
    setSelectedProjectId(proj.id);
    setCompiledSpec(proj.spec);
    setPrompt("");
    setViewMode("preview");
    
    setMessages([
      {
        id: "past-user-" + proj.id,
        sender: "user",
        text: proj.prompt,
        timestamp: proj.timestamp
      },
      {
        id: "past-ai-" + proj.id,
        sender: "ai",
        text: `Successfully reloaded your generated application **${proj.appName}** specification! You can view and manage its data tables, dynamic navigation pages, and security roles inside the preview workspace.`,
        timestamp: proj.timestamp,
        status: "completed",
        spec: proj.spec,
        tablesCount: proj.spec.db_schema?.tables?.length || 0
      }
    ]);
  };

  const handleCompile = async (customPrompt?: string) => {
    const targetPrompt = customPrompt || prompt;
    if (!targetPrompt.trim()) return;

    setLoading(true);
    setPrompt("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    const userMessageId = Math.random().toString(36).substr(2, 9);
    const aiMessageId = Math.random().toString(36).substr(2, 9);
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 1. Append User Message
    const userMsg: Message = {
      id: userMessageId,
      sender: "user",
      text: targetPrompt,
      timestamp
    };
    setMessages((prev) => [...prev, userMsg]);

    setViewMode("loading");
    const startTime = performance.now();

    try {
      setLoadingMessage("Extracting Intent...");
      await new Promise((r) => setTimeout(r, 2500));

      setLoadingMessage("Planning Application Architecture...");
      await new Promise((r) => setTimeout(r, 2500));

      setLoadingMessage("Generating Database Schema...");
      await new Promise((r) => setTimeout(r, 2500));

      // Trigger dynamic generation backend
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Gemini-API-Key": apiKey,
          "X-Gemini-Model": geminiModel,
        },
        body: JSON.stringify({ prompt: targetPrompt }),
      });

      if (!response.ok) {
        throw new Error(`Compiler backend server error: ${response.status}`);
      }

      const result = await response.json();
      const spec = result.spec;
      const errors = result.errors || [];

      // Static logical checks
      const valResponse = await fetch("http://localhost:8000/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(spec),
      });
      const valResult = await valResponse.json();
      const valErrors = valResult.errors || [];

      setCompiledSpec(spec);

      setLoadingMessage("Validating Logic Constraints...");
      await new Promise((r) => setTimeout(r, 2500));

      let heals = 0;
      if (errors.length > 0) {
        heals = errors.length;
        setLoadingMessage("Repairing Validation Anomalies...");
        await new Promise((r) => setTimeout(r, 2500));
      }

      setLoadingMessage("Compiling Live Application...");
      await new Promise((r) => setTimeout(r, 3000));
      
      setLoadingMessage("Here is your generated application!");
      await new Promise((r) => setTimeout(r, 3000));

      const endTime = performance.now();
      const finalLatency = Math.round(endTime - startTime);
      const tablesCount = spec.db_schema?.tables?.length || 0;

      // Construct a friendly, conversational summary message (no jargon, clean hierarchy)
      let summaryText = `### ✓ **${spec.app_name}** Compiled Successfully!\n\n`;
      summaryText += `I have compiled your application specification based on your prompt. Here is what has been built:\n\n`;
      
      summaryText += `* 🗄️ **Application Databases:** Created **${tablesCount} data tables** (${spec.db_schema.tables.map((t: any) => `\`${t.name}\``).join(", ")}) containing realistic seed records.\n`;
      summaryText += `* 🔌 **REST API Routes:** Configured dynamic backend endpoints supporting CRUD requests for all tables.\n`;
      summaryText += `* 🖥️ **Navigation & Pages:** Generated responsive navigation pages (${spec.ui_schema.pages.map((p: any) => `\`${p.title}\``).join(", ")}) mapped with interactive tables, forms, and analytical indicators.\n`;
      summaryText += `* 🔑 **Security & Access Control:** Configured security role authorization policy simulated for **${spec.auth_schema.roles.map((r: any) => `\`${r.role_name}\``).join(", ")}**.\n\n`;
      
      summaryText += `You can now interact with and test the live application components in the preview panel to the right!`;

      // Append final AI summary message to chat history
      const aiMsg: Message = {
        id: aiMessageId,
        sender: "ai",
        text: summaryText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        status: "completed",
        latency: finalLatency,
        tablesCount,
        repairsCount: heals,
        spec,
        errors: valErrors
      };
      setMessages((prev) => [...prev, aiMsg]);

      // Add to sidebar recent projects list
      const newProject: ProjectHistory = {
        id: Math.random().toString(36).substr(2, 9),
        prompt: targetPrompt,
        appName: spec.app_name,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        spec
      };
      setProjects((prev) => [newProject, ...prev]);
      setSelectedProjectId(newProject.id);
      setViewMode("preview");

    } catch (err: any) {
      const errorMsg: Message = {
        id: aiMessageId,
        sender: "ai",
        text: `⚠️ **Builder Compilation Failed:** ${err.message}\n\nPlease check your prompt instructions or FastAPI network logs and try again.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        status: "failed"
      };
      setMessages((prev) => [...prev, errorMsg]);
      setViewMode("chat");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleCompile();
    }
  };

  if (!hasStarted) {
    return <LandingPage onStart={() => setHasStarted(true)} />;
  }

  return (
    <div className="min-h-screen bg-[#F0FDF4] text-slate-800 flex flex-col font-sans selection:bg-emerald-500/20 antialiased overflow-hidden">
      
      {/* ==========================================
          GLOBAL HEADER (Emerald Light)
         ========================================== */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-emerald-100 px-6 py-4 flex items-center justify-between sticky top-0 z-40 h-16 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-emerald-50 border border-emerald-200 rounded-lg">
            <Icons.Sparkles className="w-4 h-4 text-emerald-600" />
          </div>
          <div>
            <h1 className="text-[10px] font-black tracking-widest text-slate-800 uppercase flex items-center gap-1.5">
              AI Software Compiler
              <span className="text-[8px] bg-emerald-100 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-mono tracking-normal">
                v2.2
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-5">
          <div className="flex items-center gap-2 text-[10px] font-black tracking-widest uppercase">
            {apiKey && apiKey.length > 5 ? (
              <>
                <span className="w-1 h-1 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-slate-500">Gemini Key:</span>
                <span className="text-emerald-600">Enabled</span>
              </>
            ) : (
              <>
                <span className="w-1 h-1 rounded-full bg-amber-500" />
                <span className="text-slate-500">Gemini Key:</span>
                <span className="font-mono text-amber-600 font-bold">Local Mock</span>
              </>
            )}
          </div>

          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`p-1.5 rounded-lg border transition-all ${
              showSettings
                ? "bg-emerald-50 border-emerald-200 text-slate-800"
                : "bg-transparent border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-100"
            }`}
            title="Configure Parameters"
          >
            <Icons.SlidersHorizontal className="w-3.5 h-3.5" />
          </button>
        </div>
      </header>

      {/* Collapsible System Options Panel */}
      {showSettings && (
        <div className="bg-white border-b border-emerald-100 px-6 py-4.5 z-40 transition-all">
          <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[9px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-1">
                <Icons.Key className="w-3 h-3 text-emerald-600" />
                Gemini API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="bg-emerald-50/50 border border-emerald-100 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-emerald-300 transition-all font-mono placeholder:text-slate-400"
                placeholder="Enter Gemini key (Leaves empty to run local mock generator)"
              />
            </div>
            
            <div className="flex flex-col gap-1.5">
              <label className="text-[9px] font-black uppercase tracking-widest text-slate-500 flex items-center gap-1">
                <Icons.Cpu className="w-3 h-3 text-emerald-600" />
                Select LLM Model
              </label>
              <select
                value={geminiModel}
                onChange={(e) => setGeminiModel(e.target.value)}
                className="bg-emerald-50/50 border border-emerald-100 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-emerald-300 transition-all cursor-pointer"
              >
                <option value="gemini-2.5-flash">gemini-2.5-flash (Standard & Balanced)</option>
                <option value="gemini-2.5-pro">gemini-2.5-pro (High Intelligence)</option>
                <option value="gemini-1.5-flash">gemini-1.5-flash (Fast)</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* ==========================================
          RESPONSIVE THREE-PANEL CONTAINER (Solid slate widths)
         ========================================== */}
      <div className="flex-1 flex overflow-x-auto overflow-y-hidden h-[calc(100vh-64px)] w-full">

        {/* -------------------------------------------
            1. LEFT PANEL: PROJECT SIDEBAR (18-20% Desktop)
           ------------------------------------------- */}
        {viewMode === "chat" && (
          <>
            <aside className="w-[18%] min-w-[280px] bg-[#F0FDF4] border-r border-emerald-100 flex flex-col p-4 overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[9px] font-black uppercase tracking-widest text-emerald-600/70 flex items-center gap-1.5">
              <Icons.FolderClosed className="w-3.5 h-3.5 text-emerald-600/70" />
              Generated Apps
            </span>
            <button
              onClick={handleStartNewProject}
              className="px-2.5 py-1 bg-white hover:bg-emerald-50 border border-emerald-200 text-emerald-700 hover:text-emerald-800 rounded-lg flex items-center gap-0.5 text-[9px] font-bold transition-all shadow-sm"
              title="Compile a fresh new app spec"
            >
              <Icons.Plus className="w-3 h-3 text-emerald-600" />
              New App
            </button>
          </div>

          {/* List of projects generated (Compact cards, no long wrapped text) */}
          <div className="flex-1 space-y-2">
            {projects.length === 0 ? (
              <div className="py-12 text-center border border-dashed border-emerald-200 rounded-2xl p-4 text-emerald-600/60 flex flex-col items-center gap-2">
                <Icons.Layers className="w-5 h-5 text-emerald-500/60" />
                <span className="text-[9px] leading-relaxed">No apps compiled yet. Submit a prompt to start building.</span>
              </div>
            ) : (
              projects.map((proj) => {
                const isActive = selectedProjectId === proj.id;
                return (
                  <button
                    key={proj.id}
                    onClick={() => loadPastProject(proj)}
                    className={`w-full text-left p-3 rounded-xl border text-xs flex flex-col gap-1 transition-all ${
                      isActive
                        ? "bg-white border-emerald-300 text-slate-900 shadow-sm shadow-emerald-500/10"
                        : "bg-transparent hover:bg-emerald-50 border-transparent text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    <span className="font-bold truncate block">{proj.appName}</span>
                    <span className="text-[8.5px] truncate block font-medium mt-0.5 opacity-70">{proj.prompt}</span>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        {/* -------------------------------------------
            2. CENTER PANEL: CHAT CONVERSATION AREA (40-42% Desktop)
           ------------------------------------------- */}
        <main className={`flex-1 ${messages.length === 0 ? "bg-gradient-to-b from-emerald-50/70 via-white to-white" : "bg-white"} flex flex-col border-r border-slate-200 relative overflow-hidden h-full`}>
          
          {/* STICKY STATUS WORKSPACE BAR (Top of conversational pane) */}
          {compiledSpec && (
            <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center justify-between text-[10px] text-slate-500 font-bold z-20 shadow-sm">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                <span>Active Spec: <strong className="text-slate-800 font-extrabold">{compiledSpec.app_name}</strong></span>
              </div>
              <div className="flex items-center gap-4 text-slate-500">
                <span>Tables: <strong className="text-slate-500">{compiledSpec.db_schema?.tables?.length || 0} compiled</strong></span>
                <span>Role Simulated: <strong className="text-emerald-600 uppercase">{activeRole}</strong></span>
              </div>
            </div>
          )}

          {/* Scrollable conversation thread */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {messages.length === 0 ? (
              /* INNER WORKSPACE EMPTY STATE */
              <div className="py-12 flex flex-col items-center justify-center h-full max-w-5xl mx-auto w-full px-6">
                

                <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-4 text-center">
                  What do you want to build today?
                </h2>
                <p className="text-slate-500 text-center mb-12 max-w-xl text-[15px] font-medium leading-relaxed">
                  Describe your ideal application below. The more detailed your prompt, the better the generated mock data and components will be.
                </p>

                {/* Base44 Style Large Central Input */}
                <div className="w-full max-w-[700px] bg-white border border-slate-200 rounded-[28px] p-3 shadow-lg shadow-emerald-900/5 flex flex-col gap-2 relative focus-within:border-emerald-300 transition-all focus-within:shadow-xl mb-14">
                  <textarea
                    ref={textareaRef}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Design a personal budget tracker with charts..."
                    className="w-full bg-transparent border-0 outline-none text-[16px] text-slate-800 placeholder-slate-400 resize-none min-h-[80px] p-4 font-medium"
                  />
                  <div className="flex items-center justify-end px-4 pb-2 pt-1">
                    <div className="flex items-center gap-4">
                      <button
                        onClick={() => handleCompile()}
                        disabled={loading || !prompt.trim()}
                        className="bg-[#10B981] hover:bg-[#059669] text-white w-10 h-10 rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:scale-100 active:scale-95 shadow-md border border-[#059669]"
                      >
                        {loading ? <Icons.Loader2 className="w-5 h-5 animate-spin" /> : <Icons.ArrowUp className="w-5 h-5" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Pill Suggestions */}
                <div className="text-center w-full max-w-4xl flex flex-col items-center">
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-6 block">
                    NOT SURE WHERE TO START? TRY ONE OF THESE:
                  </span>
                  <div className="flex flex-wrap justify-center gap-3.5">
                    <button onClick={() => selectExample("Build a CRM Reporting Dashboard")} className="px-5 py-2.5 bg-transparent border border-slate-200 rounded-full text-slate-600 text-[13px] font-medium hover:border-emerald-300 hover:bg-white hover:text-emerald-700 transition-all shadow-sm">Reporting Dashboard</button>
                    <button onClick={() => selectExample("Build a Hospital Clinic Management Platform")} className="px-5 py-2.5 bg-transparent border border-slate-200 rounded-full text-slate-600 text-[13px] font-medium hover:border-emerald-300 hover:bg-white hover:text-emerald-700 transition-all shadow-sm">Clinic Platform</button>
                    <button onClick={() => selectExample("Build an Employee Onboarding Portal")} className="px-5 py-2.5 bg-transparent border border-slate-200 rounded-full text-slate-600 text-[13px] font-medium hover:border-emerald-300 hover:bg-white hover:text-emerald-700 transition-all shadow-sm">Onboarding Portal</button>
                    <button onClick={() => selectExample("Build an Inventory Tracking System")} className="px-5 py-2.5 bg-transparent border border-slate-200 rounded-full text-slate-600 text-[13px] font-medium hover:border-emerald-300 hover:bg-white hover:text-emerald-700 transition-all shadow-sm">Inventory System</button>
                    <button onClick={() => selectExample("Build a Learning Management System")} className="px-5 py-2.5 bg-transparent border border-slate-200 rounded-full text-slate-600 text-[13px] font-medium hover:border-emerald-300 hover:bg-white hover:text-emerald-700 transition-all shadow-sm">LMS Platform</button>
                  </div>
                </div>

              </div>
            ) : (
              /* Conversational Thread listing */
              <div className="space-y-6">
                {messages.map((msg) => {
                  const isUser = msg.sender === "user";
                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-3.5 max-w-2xl ${
                        isUser ? "ml-auto flex-row-reverse" : "mr-auto"
                      }`}
                    >
                      {/* Avatar bubbles */}
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm ${
                        isUser 
                          ? "bg-white border border-slate-200 text-slate-500"
                          : "bg-emerald-50 border border-emerald-200 text-emerald-600"
                      }`}>
                        {isUser ? (
                          <Icons.User className="w-4 h-4" />
                        ) : (
                          <Icons.Sparkles className="w-4 h-4 text-emerald-600" />
                        )}
                      </div>

                      {/* Content balloons */}
                      <div className="flex flex-col gap-2.5 flex-1 max-w-[85%]">
                        <div className={`p-4 rounded-xl text-xs leading-relaxed shadow-sm ${
                          isUser
                            ? "bg-white border border-slate-200 text-slate-800 rounded-tr-none"
                            : "bg-emerald-50/50 border border-emerald-100 text-slate-700 rounded-tl-none"
                        }`}>
                          {/* Markdown parsing for bullet lists */}
                          {msg.text.split("\n\n").map((paragraph, idx) => {
                            if (paragraph.startsWith("###")) {
                              return (
                                <h4 key={idx} className="font-extrabold text-[12px] text-emerald-600 mb-2 mt-1 uppercase tracking-wider">
                                  {paragraph.replace("###", "").trim()}
                                </h4>
                              );
                            }
                            if (paragraph.startsWith("*")) {
                              return (
                                <ul key={idx} className="space-y-1.5 my-2">
                                  {paragraph.split("\n").map((li, lidx) => (
                                    <li key={lidx} className="flex items-start gap-1">
                                      <span className="text-emerald-500 mt-0.5 flex-shrink-0">✓</span>
                                      <span className="leading-relaxed">{li.replace("*", "").trim()}</span>
                                    </li>
                                  ))}
                                </ul>
                              );
                            }
                            return <p key={idx} className="mb-2 leading-relaxed font-medium">{paragraph}</p>;
                          })}

                          {/* Dynamic telemetry footer info for finished compilation */}
                          {!isUser && msg.status === "completed" && (
                            <div className="flex items-center gap-3 pt-3 mt-3 border-t border-emerald-100 text-[9px] font-mono text-slate-500 font-bold">
                              <span>Latency: <strong>{msg.latency}ms</strong></span>
                              <span>•</span>
                              <span>Data Tables: <strong>{msg.tablesCount} active</strong></span>
                              {msg.repairsCount && msg.repairsCount > 0 ? (
                                <>
                                  <span>•</span>
                                  <span className="text-amber-600">Heals: <strong>{msg.repairsCount} triggers</strong></span>
                                </>
                              ) : null}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={chatEndRef} />
              </div>
            )}

          </div>

          {/* 5. PROMPT INPUT: Fixed at bottom */}
          {messages.length > 0 && (
            <div className="p-4 bg-white/90 backdrop-blur-sm border-t border-slate-200">
              <div className="max-w-xl mx-auto bg-slate-50 border border-slate-200 rounded-2xl p-3 flex flex-col gap-2 relative focus-within:border-emerald-300 focus-within:shadow-md transition-all">
                <textarea
                  ref={textareaRef}
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Evolve or compile software (e.g. 'Build CRM', 'Add subscription billing')..."
                  className="w-full bg-transparent border-0 outline-none text-xs text-slate-800 placeholder-slate-500 resize-none min-h-[45px] max-h-[140px] py-1 font-medium"
                  rows={1}
                  disabled={loading}
                />

                <div className="flex items-center justify-between pt-1 border-t border-slate-200">
                  <div className="flex items-center gap-1 text-[9px] text-slate-400 font-bold">
                    <Icons.CornerDownLeft className="w-3.5 h-3.5" />
                    <span>Enter to compile</span>
                  </div>

                  <button
                    onClick={() => handleCompile()}
                    disabled={loading || !prompt.trim()}
                    className="bg-[#10B981] hover:bg-[#059669] text-white font-black px-3.5 py-1.5 rounded-xl text-[9px] uppercase tracking-wider flex items-center gap-1 transition-all disabled:opacity-20 disabled:scale-100 active:scale-[0.98] border border-[#059669]"
                  >
                    {loading ? (
                      <>
                        <Icons.Loader2 className="w-3 h-3 animate-spin text-white" />
                        <span>Compiling...</span>
                      </>
                    ) : (
                      <>
                        <Icons.Send className="w-3 h-3 text-indigo-600" />
                        <span>Compile</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

        </main>
          </>
        )}

        {/* -------------------------------------------
            3. FULL-SCREEN CINEMATIC LOADING SEQUENCE
           ------------------------------------------- */}
        {viewMode === "loading" && (
          <section className="absolute inset-0 z-50 bg-gradient-to-b from-emerald-50 to-white flex flex-col items-center justify-center p-6 animate-in fade-in duration-500">
            <div className="max-w-md w-full flex flex-col items-center gap-8 -mt-10">
              <div className="relative w-24 h-24 flex items-center justify-center">
                <div className="absolute inset-0 border-[6px] border-emerald-100 rounded-full"></div>
                <div className="absolute inset-0 border-[6px] border-emerald-500 rounded-full border-t-transparent shadow-[0_0_15px_rgba(16,185,129,0.3)] animate-spin"></div>
                <Icons.Sparkles className="w-8 h-8 text-emerald-500 animate-pulse" />
              </div>
              <div className="h-12 flex items-center justify-center overflow-hidden w-full">
                <h2 className={`text-[28px] font-medium text-slate-800 tracking-tight text-center transition-all duration-700 transform ${fade ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                  {displayMessage}
                </h2>
              </div>
            </div>
          </section>
        )}

        {/* -------------------------------------------
            4. FULL-SCREEN LIVE APP PREVIEW AREA
           ------------------------------------------- */}
        {viewMode === "preview" && (
          <section className="flex-1 bg-slate-50 flex flex-col p-6 overflow-y-auto h-full gap-4 animate-in fade-in zoom-in-95 duration-500">
          
          <div className="flex border-b border-slate-200 pb-1.5 gap-3.5 items-center justify-between">
            <div className="flex gap-3.5">
              <button
                onClick={() => setActiveTab("preview")}
                className={`pb-2 font-black text-[10px] uppercase tracking-widest transition-all ${
                  activeTab === "preview"
                    ? "text-indigo-600 border-b border-indigo-400"
                    : "text-slate-500 hover:text-slate-500"
                }`}
              >
                🚀 App Preview
              </button>
              <button
                onClick={() => setActiveTab("schema")}
                className={`pb-2 font-black text-[10px] uppercase tracking-widest transition-all ${
                  activeTab === "schema"
                    ? "text-indigo-600 border-b border-indigo-400"
                    : "text-slate-500 hover:text-slate-500"
                }`}
              >
                📄 AST Schema
              </button>
            </div>
            <button 
              onClick={() => setViewMode("chat")} 
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 hover:border-slate-300 rounded-lg text-[10px] font-bold text-slate-600 hover:text-slate-900 shadow-sm transition-all mb-2"
            >
              <Icons.ArrowLeft className="w-3.5 h-3.5" />
              Back to Chat
            </button>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            {activeTab === "preview" ? (
              /* REAL APPLICATION PREVIEW view container */
              <div className="flex-1 bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-lg flex flex-col min-h-[500px]">
                
                {/* UPGRADED ADDRESS NAVIGATION BAR MOCK */}
                <div className="bg-slate-50 border-b border-slate-200 px-4 py-2 flex items-center justify-between z-10 shadow-sm">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-850" />
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-850" />
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-850" />
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="bg-[#080B12] border border-slate-200 text-[9.5px] text-slate-500 rounded-lg px-3 py-1 flex items-center justify-center font-mono w-56 shadow-inner">
                      <Icons.Lock className="w-3 h-3 text-emerald-500 mr-1.5 flex-shrink-0" />
                      localhost:3000
                    </div>

                    <button 
                      onClick={() => handleCompile(messages[messages.length - 2]?.text)} 
                      className="p-1 hover:bg-white rounded text-slate-500 hover:text-slate-500 transition-colors"
                      title="Reload workspace"
                      disabled={loading || messages.length === 0}
                    >
                      <Icons.RotateCw className="w-3 h-3" />
                    </button>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-[8px] bg-slate-50 text-indigo-600 border border-slate-200 px-1.5 py-0.5 rounded font-mono font-bold tracking-normal uppercase">
                      ROLE: {activeRole}
                    </span>
                  </div>
                </div>

                <div className="flex-1 p-3 bg-white flex flex-col justify-center overflow-y-auto">
                  {compiledSpec ? (
                    <SchemaInterpreter
                      spec={compiledSpec}
                      activeRole={activeRole}
                      setActiveRole={setActiveRole}
                    />
                  ) : (
                    /* Real Premium Looking Mock Empty State Dashboard (Slate styled placeholder) */
                    <div className="flex flex-col gap-5 p-4 py-10 max-w-md mx-auto w-full">
                      <div className="text-center space-y-1.5">
                        {loading ? (
                          <>
                            <Icons.Loader2 className="w-6.5 h-6.5 text-indigo-500 mx-auto animate-spin" />
                            <h4 className="text-xs font-bold text-indigo-600 animate-pulse">
                              Compiling Live Interface...
                            </h4>
                            <p className="text-[9.5px] text-slate-500 max-w-xs mx-auto leading-relaxed font-semibold">
                              Building databases, routing REST APIs, and generating UI components dynamically.
                            </p>
                          </>
                        ) : (
                          <>
                            <Icons.MonitorPlay className="w-6.5 h-6.5 text-slate-500 mx-auto" />
                            <h4 className="text-xs font-bold text-slate-500">
                              Your generated application will appear here
                            </h4>
                            <p className="text-[9.5px] text-slate-500 max-w-xs mx-auto leading-relaxed font-semibold">
                              Once compiled, complete functional pages, tables with seed data, forms, and analytical grids will load dynamically.
                            </p>
                          </>
                        )}
                      </div>

                      {/* Mock dynamic preview container overlaying placeholder widgets (Spacious, high-fidelity slate) */}
                      <div className={`border border-slate-200 rounded-xl p-4 bg-slate-50/40 flex flex-col gap-3.5 select-none pointer-events-none scale-[0.98] transition-all duration-500 ${loading ? "opacity-70 animate-pulse shadow-inner" : "opacity-25"}`}>
                        
                        {/* Mock Nav */}
                        <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                          <div className="flex items-center gap-1.5">
                            <div className="w-4 h-4 rounded bg-white" />
                            <div className="w-16 h-2.5 bg-white rounded" />
                          </div>
                          <div className="flex gap-2">
                            <div className="w-8 h-2 bg-slate-50 rounded" />
                            <div className="w-8 h-2 bg-slate-50 rounded" />
                          </div>
                        </div>

                        {/* Mock Metrics */}
                        <div className="grid grid-cols-2 gap-2.5">
                          <div className="border border-slate-200 rounded-lg p-2.5 bg-[#1F2937]/35 space-y-1.5">
                            <div className="w-10 h-1.5 bg-slate-850 rounded" />
                            <div className="w-16 h-3 bg-white rounded" />
                          </div>
                          <div className="border border-slate-200 rounded-lg p-2.5 bg-[#1F2937]/35 space-y-1.5">
                            <div className="w-10 h-1.5 bg-slate-850 rounded" />
                            <div className="w-12 h-3 bg-white rounded" />
                          </div>
                        </div>

                        {/* Mock Table */}
                        <div className="border border-slate-200 rounded-lg p-2.5 bg-slate-50/30 space-y-2">
                          <div className="w-16 h-2 bg-white rounded mb-1" />
                          <div className="space-y-1.5">
                            <div className="flex justify-between">
                              <div className="w-24 h-1.5 bg-slate-50 rounded" />
                              <div className="w-8 h-1.5 bg-slate-50 rounded" />
                            </div>
                            <div className="flex justify-between">
                              <div className="w-20 h-1.5 bg-slate-50 rounded" />
                              <div className="w-10 h-1.5 bg-slate-50 rounded" />
                            </div>
                          </div>
                        </div>

                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* Structured AST Schema JSON view */
              <div className="flex-1 bg-slate-50/40 border border-slate-200 rounded-2xl p-4 flex flex-col gap-3 shadow-md min-h-[500px]">
                <div className="flex bg-white border border-slate-200 p-1 rounded-xl w-fit gap-1 text-[9px] font-black uppercase tracking-wider shadow-inner">
                  {(["ui", "api", "db", "auth"] as const).map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveSchemaTab(tab)}
                      className={`px-2.5 py-1.5 rounded-lg transition-all ${
                        activeSchemaTab === tab
                          ? "bg-slate-850 text-indigo-600 shadow"
                          : "text-slate-500 hover:text-slate-500"
                      }`}
                    >
                      {tab} Spec
                    </button>
                  ))}
                </div>

                <div className="flex-1 bg-white rounded-xl p-4 border border-slate-200 max-h-[460px] overflow-y-auto">
                  {compiledSpec ? (
                    <pre className="text-[10px] font-mono text-slate-500 leading-relaxed">
                      {JSON.stringify(
                        activeSchemaTab === "ui"
                          ? compiledSpec.ui_schema
                          : activeSchemaTab === "api"
                            ? compiledSpec.api_schema
                            : activeSchemaTab === "db"
                              ? compiledSpec.db_schema
                              : compiledSpec.auth_schema,
                        null,
                        2
                      )}
                    </pre>
                  ) : (
                    <span className="text-[9.5px] text-slate-500 font-mono italic">No AST schemas compiled. Describe your app to begin.</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </section>
        )}
      </div>
    </div>
  );
}
