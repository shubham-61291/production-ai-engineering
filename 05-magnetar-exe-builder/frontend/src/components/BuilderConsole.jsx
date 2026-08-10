import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Sparkles, Terminal, Shield, Code, Cpu } from 'lucide-react';

const PRESETS = [
  {
    title: "Tkinter System Monitor GUI",
    desc: "Desktop app with real-time CPU, RAM, disk gauges and dark sleek theme",
    prompt: "Build a modern Tkinter desktop GUI application that displays real-time CPU usage, RAM utilization, and Disk space gauges using psutil. Includes dark mode theme and exit button."
  },
  {
    title: "AES File Encrypter GUI",
    desc: "Desktop encryption tool for secure file locking and unlocking",
    prompt: "Create a Tkinter GUI file encrypter and decrypter using cryptography library. Users can select a file, enter a password, and encrypt/decrypt with AES-256."
  },
  {
    title: "Scientific Calculator GUI",
    desc: "GUI calculator supporting trigonometric & logarithmic operations",
    prompt: "Develop a scientific calculator desktop application using Tkinter with buttons for sin, cos, tan, log, square root, power, clear, and basic arithmetic operations."
  },
  {
    title: "Web Scraper & Report CLI",
    desc: "CLI tool that fetches web content and outputs structured JSON report",
    prompt: "Write a command-line Python application that accepts a target URL, extracts page title, meta description, all header tags (H1-H3), links count, and exports report to JSON."
  }
];

export default function BuilderConsole({ onStartBuild, isBuilding }) {
  const [requirements, setRequirements] = useState(
    "Build a modern Tkinter desktop GUI application that displays real-time CPU usage, RAM utilization, and Disk space gauges. Include smooth updates and dark mode styling."
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!requirements.trim() || isBuilding) return;
    onStartBuild(requirements);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      className="w-full max-w-4xl mx-auto glass-panel-glow rounded-2xl p-6 md:p-8 relative overflow-hidden my-6"
    >
      {/* Top bar header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-wide">
              Agentic Windows Executable Architect
            </h2>
            <p className="text-xs text-slate-400">
              Powered by Qwen2.5-Coder 32B ReAct Engine & In-Code PyInstaller Build Pipeline
            </p>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
          <Terminal className="w-3.5 h-3.5 text-purple-400" />
          <span>Local GPU Compiler</span>
        </div>
      </div>

      {/* Preset cards */}
      <div className="mb-6">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2.5 block">
          Quick Preset Blueprints
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {PRESETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setRequirements(preset.prompt)}
              className="text-left p-3.5 rounded-xl bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/40 transition-all group"
            >
              <div className="text-sm font-semibold text-cyan-300 group-hover:text-cyan-200 flex items-center justify-between">
                <span>{preset.title}</span>
                <Code className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-purple-400" />
              </div>
              <div className="text-xs text-slate-400 mt-1 line-clamp-2">
                {preset.desc}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2 block flex items-center justify-between">
            <span>Specify App Requirements</span>
            <span className="text-[11px] text-cyan-400 font-normal lowercase">Includes auto-copyright notice</span>
          </label>
          <textarea
            rows={5}
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            disabled={isBuilding}
            placeholder="Describe the Windows application you want Qwen2.5-Coder to build..."
            className="w-full rounded-xl bg-slate-950/80 border border-slate-700/80 p-4 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 font-mono transition-all resize-none shadow-inner"
          />
        </div>

        {/* Action button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isBuilding || !requirements.trim()}
            className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm tracking-wide flex items-center justify-center gap-3 transition-all shadow-lg ${
              isBuilding
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                : 'bg-gradient-to-r from-cyan-500 via-purple-600 to-pink-600 hover:from-cyan-400 hover:via-purple-500 hover:to-pink-500 text-white shadow-cyan-500/25 hover:shadow-cyan-500/40 active:scale-95'
            }`}
          >
            {isBuilding ? (
              <>
                <Cpu className="w-4 h-4 animate-spin text-cyan-400" />
                <span>BUILDING WINDOWS EXE...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                <span>GENERATE & COMPILE APP.EXE</span>
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
