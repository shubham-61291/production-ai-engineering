import React from 'react';
import { motion } from 'framer-motion';
import { Download, CheckCircle2, ShieldCheck, FileCheck, Sparkles } from 'lucide-react';

export default function DownloadSection({ runId, exeReady }) {
  if (!exeReady || !runId) return null;

  const downloadUrl = `/api/download/${runId}`;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="w-full max-w-4xl mx-auto glass-panel-glow rounded-2xl p-6 md:p-8 text-center my-6 relative overflow-hidden bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-purple-950/40 border border-emerald-500/40"
    >
      <div className="flex justify-center mb-4">
        <div className="p-4 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-400 animate-bounce">
          <CheckCircle2 className="w-10 h-10" />
        </div>
      </div>

      <h3 className="text-2xl font-extrabold text-white tracking-wide mb-2">
        Windows Executable Successfully Built!
      </h3>
      <p className="text-sm text-slate-300 max-w-xl mx-auto mb-6">
        Your standalone Windows executable <code className="bg-slate-800 text-cyan-300 px-2 py-0.5 rounded border border-slate-700 font-mono">app.exe</code> has been packaged with all dependencies and is ready for immediate deployment.
      </p>

      {/* Metadata Badges */}
      <div className="flex flex-wrap justify-center gap-4 text-xs font-mono text-slate-300 mb-8">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <FileCheck className="w-4 h-4 text-cyan-400" />
          <span>Artifact: <strong className="text-white">app.exe</strong></span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>PyInstaller Sandbox Verified</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span>Target OS: <strong className="text-white">Windows (x64)</strong></span>
        </div>
      </div>

      {/* Download Action Button */}
      <div className="flex justify-center">
        <a
          href={downloadUrl}
          download="app.exe"
          className="inline-flex items-center gap-3 px-10 py-4 rounded-xl font-extrabold text-base tracking-wide bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:via-teal-400 hover:to-cyan-400 text-black shadow-[0_0_30px_rgba(16,185,129,0.4)] hover:shadow-[0_0_40px_rgba(16,185,129,0.6)] transition-all transform hover:-translate-y-0.5 active:translate-y-0"
        >
          <Download className="w-5 h-5 text-black stroke-[3]" />
          <span>DOWNLOAD APP.EXE</span>
        </a>
      </div>
    </motion.div>
  );
}
