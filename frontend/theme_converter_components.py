import re
import glob
import os

files = glob.glob(r"d:\CRM AI PIPELINE\frontend\src\components\*.tsx") + glob.glob(r"d:\CRM AI PIPELINE\frontend\src\runtime\*.tsx")

replacements = {
    r'bg-slate-950': 'bg-white',
    r'bg-slate-900': 'bg-slate-50',
    r'bg-slate-800': 'bg-slate-100',
    r'border-slate-800': 'border-slate-200',
    r'border-slate-700': 'border-slate-200',
    r'text-slate-100': 'text-slate-900',
    r'text-slate-200': 'text-slate-800',
    r'text-slate-300': 'text-slate-700',
    r'text-slate-400': 'text-slate-500',
    r'to-slate-400': 'to-slate-600',
    r'text-indigo-400': 'text-indigo-600',
    r'bg-indigo-500/20': 'bg-indigo-100',
    r'text-emerald-400': 'text-emerald-600',
    r'hover:bg-slate-800': 'hover:bg-slate-200',
    r'shadow-2xl': 'shadow-sm',
    # Specific darker theme overrides
    r'bg-\[\#080B10\]': 'bg-white',
    r'bg-\[\#0F172A\]': 'bg-slate-50',
    r'bg-\[\#111827\]': 'bg-slate-50',
    r'bg-\[\#1E293B\]': 'bg-white',
}

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    if original_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(filepath)}")

print("Global theme conversion complete for components.")
