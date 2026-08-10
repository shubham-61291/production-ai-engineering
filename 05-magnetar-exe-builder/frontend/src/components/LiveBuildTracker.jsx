import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { Terminal, Code, CheckCircle, AlertCircle, Loader2, FileCode, Package, Layers } from 'lucide-react';

const STAGES = [
  { id: 'scaffold', label: '1. Scaffold' },
  { id: 'codegen', label: '2. Qwen2.5 Codegen' },
  { id: 'sanity', label: '3. Sanity Check' },
  { id: 'patch', label: '4. Auto Repair' },
  { id: 'compile', label: '5. PyInstaller Build' },
  { id: 'ready', label: '6. EXE Ready' }
];

export default function LiveBuildTracker({ status, logs, mainPy, requirementsTxt, isBuilding, exeReady }) {
  const [activeTab, setActiveTab] = useState('terminal');
  const terminalEndRef = useRef(null);

  useEffect(() => {
    if (activeTab === 'terminal') {
      terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, activeTab]);

  const getStageStatus = (stageId) => {
    const s = (status || '').toLowerCase();
    if (s.includes('error') || s.includes('failed')) return 'error';
    if (exeReady || s.includes('done') || s.includes('exe ready')) return 'completed';

    if (stageId === 'scaffold') {
      return s.includes('initializing') || s.includes('workspace') ? 'active' : 'completed';
    }
    if (stageId === 'codegen') {
      if (s.includes('react') || s.includes('codegen') || s.includes('thinking')) return 'active';
      if (s.includes('sanity') || s.includes('compiling') || s.includes('patch') || s.includes('exe ready')) return 'completed';
      return 'pending';
    }
    if (stageId === 'sanity') {
      if (s.includes('sanity check') || s.includes('sanity...')) return 'active';
      if (s.includes('patch') || s.includes('compiling') || s.includes('exe ready')) return 'completed';
      return 'pending';
    }
    if (stageId === 'patch') {
      if (s.includes('patching') || s.includes('patch round')) return 'active';
      if (s.includes('compiling') || s.includes('exe ready')) return 'completed';
      return 'pending';
    }
    if (stageId === 'compile') {
      if (s.includes('compiling') || s.includes('pyinstaller')) return 'active';
      if (exeReady || s.includes('exe ready')) return 'completed';
      return 'pending';
    }
    if (stageId === 'ready') {
      return exeReady ? 'completed' : 'pending';
    }
    return 'pending';
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, delay: 0.2 }}
      className="w-full max-w-4xl mx-auto glass-panel rounded-2xl p-6 relative my-6"
    >
      {/* Stage Stepper Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Agent Pipeline Execution Engine</span>
          </div>
          <div className="text-xs text-slate-400 font-mono">
            Status: <span className="text-cyan-300 font-semibold">{status || 'Idle'}</span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2">
          {STAGES.map((st) => {
            const stState = getStageStatus(st.id);
            return (
              <div 
                key={st.id}
                className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center justify-between transition-all ${
                  stState === 'completed'
                    ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                    : stState === 'active'
                    ? 'bg-cyan-950/60 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(56,189,248,0.3)] animate-pulse'
                    : stState === 'error'
                    ? 'bg-rose-950/50 border-rose-500/40 text-rose-300'
                    : 'bg-slate-900/40 border-slate-800 text-slate-500'
                }`}
              >
                <span className="truncate">{st.label}</span>
                {stState === 'completed' && <CheckCircle className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 ml-1" />}
                {stState === 'active' && <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin flex-shrink-0 ml-1" />}
                {stState === 'error' && <AlertCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0 ml-1" />}
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabs Selector */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-4">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('terminal')}
            className={`px-4 py-2 rounded-lg text-xs font-mono flex items-center gap-2 transition-all ${
              activeTab === 'terminal'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Live Logs ({logs ? logs.split('\n').length : 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('main_py')}
            disabled={!mainPy}
            className={`px-4 py-2 rounded-lg text-xs font-mono flex items-center gap-2 transition-all ${
              activeTab === 'main_py'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : mainPy ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 cursor-not-allowed'
            }`}
          >
            <FileCode className="w-3.5 h-3.5" />
            <span>src/main.py</span>
          </button>

          <button
            onClick={() => setActiveTab('requirements')}
            disabled={!requirementsTxt}
            className={`px-4 py-2 rounded-lg text-xs font-mono flex items-center gap-2 transition-all ${
              activeTab === 'requirements'
                ? 'bg-slate-800 text-cyan-400 border border-slate-700'
                : requirementsTxt ? 'text-slate-400 hover:text-slate-200' : 'text-slate-600 cursor-not-allowed'
            }`}
          >
            <Package className="w-3.5 h-3.5" />
            <span>requirements.txt</span>
          </button>
        </div>
      </div>

      {/* Content display panel */}
      <div className="h-80 w-full rounded-xl bg-slate-950/90 border border-slate-800 p-4 font-mono text-xs overflow-y-auto leading-relaxed shadow-inner">
        {activeTab === 'terminal' && (
          <div className="space-y-1">
            {logs ? (
              logs.split('\n').map((line, idx) => (
                <div key={idx} className={`whitespace-pre-wrap ${
                  line.includes('ERROR') || line.includes('FAILED')
                    ? 'text-rose-400'
                    : line.includes('SUCCESS') || line.includes('passed')
                    ? 'text-emerald-400 font-semibold'
                    : line.includes('Tool call')
                    ? 'text-cyan-300'
                    : line.includes('ReAct')
                    ? 'text-purple-300'
                    : 'text-slate-300'
                }`}>
                  {line}
                </div>
              ))
            ) : (
              <span className="text-slate-600 italic">No agent logs generated yet. Click "BUILD WINDOWS EXE" to initiate agent execution engine.</span>
            )}
            <div ref={terminalEndRef} />
          </div>
        )}

        {activeTab === 'main_py' && (
          <pre className="text-emerald-300 font-mono whitespace-pre-wrap">
            {mainPy || '# src/main.py will appear here after ReAct code generation...'}
          </pre>
        )}

        {activeTab === 'requirements' && (
          <pre className="text-purple-300 font-mono whitespace-pre-wrap">
            {requirementsTxt || '# requirements.txt will appear here...'}
          </pre>
        )}
      </div>
    </motion.div>
  );
}
