import React from 'react';
import { Cpu, Settings, CheckCircle2, XCircle } from 'lucide-react';

export default function Header({ health, onOpenSettings }) {
  const ollamaOnline = health?.ollama_online;
  const modelName = health?.default_model || 'qwen2.5-coder:32b';

  return (
    <header className="relative z-20 flex flex-wrap justify-between items-center px-6 md:px-10 py-5 bg-gradient-to-b from-black/90 via-black/50 to-transparent backdrop-blur-sm border-b border-white/10">
      {/* Brand & Logo */}
      <div className="flex items-center gap-4">
        <img 
          src="https://res.cloudinary.com/dud3yhilm/image/upload/v1761113319/Gemini_Generated_Image_f6b5ff6b5ff6b5ff_aqa9q6.png" 
          alt="Application EXE Builder Logo" 
          className="h-10 md:h-12 w-auto object-contain drop-shadow-[0_0_12px_rgba(56,189,248,0.5)]" 
        />
        <div>
          <h1 className="text-xl md:text-2xl font-extrabold tracking-wide bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
            Application EXE Builder
          </h1>
          <p className="text-xs text-slate-300 font-medium tracking-tight -mt-0.5">
            Engineering the Path to Singularity — Qwen2.5-Coder In-Code Compiler
          </p>
        </div>
      </div>

      {/* Connection Badges & Settings Button */}
      <div className="flex items-center gap-4 mt-3 sm:mt-0">
        {/* Model status pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/80 border border-slate-700/60 text-xs font-mono text-slate-200">
          <Cpu className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span className="text-slate-400">LLM:</span>
          <span className="text-cyan-300 font-semibold">{modelName}</span>
          {ollamaOnline ? (
            <span className="flex items-center gap-1 text-emerald-400 text-[11px] ml-1 bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-500/30">
              <CheckCircle2 className="w-3 h-3" /> GPU Online
            </span>
          ) : (
            <span className="flex items-center gap-1 text-amber-400 text-[11px] ml-1 bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-500/30">
              <XCircle className="w-3 h-3" /> Offline
            </span>
          )}
        </div>

        {/* Settings button */}
        <button
          onClick={onOpenSettings}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-all border border-slate-700/60 hover:border-cyan-500/50 shadow-md"
          title="Open Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
