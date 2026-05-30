import re

with open(r"d:\CRM AI PIPELINE\frontend\src\App.tsx", "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    # Backgrounds
    r'bg-\[\#080B10\]': 'bg-white', # Main background
    r'bg-\[\#0F172A\]': 'bg-white', # Header
    r'bg-\[\#111827\]/70': 'bg-white',
    r'bg-\[\#111827\]': 'bg-slate-50', # Sidebar / panels
    r'bg-\[\#1E293B\]': 'bg-white',
    r'bg-\[\#0E1524\]': 'bg-white', # Center panel
    r'bg-\[\#0A0F1D\]': 'bg-slate-50', # Right panel
    
    r'bg-slate-950': 'bg-white',
    r'bg-slate-900': 'bg-slate-50',
    r'bg-slate-800': 'bg-white',
    
    r'hover:bg-\[\#111827\]': 'hover:bg-slate-50',
    r'hover:bg-slate-850': 'hover:bg-slate-100',
    r'hover:bg-slate-800': 'hover:bg-slate-100',
    
    # Borders
    r'border-slate-800/80': 'border-slate-200',
    r'border-slate-900/60': 'border-slate-200',
    r'border-slate-900/40': 'border-slate-200',
    r'border-slate-700/50': 'border-slate-200',
    r'border-slate-700/85': 'border-slate-300',
    r'border-slate-850': 'border-slate-200',
    r'border-slate-900': 'border-slate-200',
    r'border-slate-800': 'border-slate-200',
    r'border-slate-700': 'border-slate-200',
    r'border-slate-950': 'border-slate-200',
    
    r'hover:border-slate-800': 'hover:border-slate-300',
    r'hover:border-slate-700': 'hover:border-slate-300',
    
    # Text colors
    r'text-\[\#E2E8F0\]': 'text-slate-900',
    r'text-\[\#F1F5F9\]': 'text-slate-900',
    r'text-slate-100': 'text-slate-900',
    r'text-slate-200': 'text-slate-800',
    r'text-slate-300': 'text-slate-700',
    r'text-slate-350': 'text-slate-700',
    r'text-slate-400': 'text-slate-500',
    r'text-slate-550': 'text-slate-500',
    r'text-slate-600': 'text-slate-500',
    r'text-slate-650': 'text-slate-500',
    r'text-slate-700': 'text-slate-500',
    r'hover:text-white': 'hover:text-slate-900',
    r'hover:text-slate-200': 'hover:text-slate-800',
    r'hover:text-slate-350': 'hover:text-slate-600',
    
    # Accents
    r'text-indigo-400': 'text-indigo-600',
    r'hover:text-indigo-400': 'hover:text-indigo-700',
    r'text-teal-400': 'text-teal-700',
    r'text-amber-400': 'text-amber-600',
    r'text-amber-500': 'text-amber-600',
    r'text-emerald-400': 'text-emerald-700',
    
    # Selection
    r'selection:bg-teal-500/20': 'selection:bg-indigo-500/20',
    
    # Avatars/Bubbles
    r'bg-emerald-950/60': 'bg-emerald-50',
    r'text-emerald-450': 'text-emerald-700',
    r'border-emerald-900/20': 'border-emerald-200',
    
    r'bg-amber-950/60': 'bg-amber-50',
    r'text-amber-450': 'text-amber-700',
    r'border-amber-900/20': 'border-amber-200',
    
    r'bg-red-950/60': 'bg-red-50',
    r'text-red-455': 'text-red-700',
    r'border-red-900/20': 'border-red-200',

    # Specific tweaks for light mode bubbles
    # User bubble background
    r'bg-\[\#1E293B\] border border-slate-800 text-slate-200': 'bg-slate-100 border border-slate-200 text-slate-800',
    # AI bubble background
    r'bg-\[\#111827\] border border-slate-850 text-slate-300': 'bg-white border border-slate-200 text-slate-700',
}

for pattern, replacement in replacements.items():
    content = re.sub(pattern, replacement, content)

with open(r"d:\CRM AI PIPELINE\frontend\src\App.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("Theme conversion complete.")
