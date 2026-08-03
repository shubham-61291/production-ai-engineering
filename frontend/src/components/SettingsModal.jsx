import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Save, Cpu, Key, Globe, Shield } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, settings, onSaveSettings }) {
  const [provider, setProvider] = useState(settings?.provider || 'ollama');
  const [baseUrl, setBaseUrl] = useState(settings?.base_url || 'http://localhost:11434');
  const [model, setModel] = useState(settings?.model || 'qwen2.5-coder:32b');
  const [apiKey, setApiKey] = useState(settings?.api_key || '');

  if (!isOpen) return null;

  const handleSave = (e) => {
    e.preventDefault();
    onSaveSettings({
      provider,
      base_url: baseUrl,
      model,
      api_key: apiKey
    });
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="w-full max-w-lg glass-panel-glow rounded-2xl p-6 md:p-8 relative bg-slate-950/95 border border-slate-700/80 shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-6">
            <div className="flex items-center gap-2.5">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <h3 className="text-lg font-bold text-white tracking-wide">
                Engine & LLM Settings
              </h3>
            </div>
            <button 
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSave} className="space-y-5">
            {/* Provider Selector */}
            <div>
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 block">
                Execution Provider
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setProvider('ollama')}
                  className={`p-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    provider === 'ollama'
                      ? 'bg-cyan-950/80 border-cyan-400 text-cyan-300 shadow-[0_0_15px_rgba(56,189,248,0.2)]'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  <Cpu className="w-4 h-4" />
                  <span>Ollama (Local GPU)</span>
                </button>

                <button
                  type="button"
                  onClick={() => setProvider('openai')}
                  className={`p-3 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    provider === 'openai'
                      ? 'bg-purple-950/80 border-purple-400 text-purple-300 shadow-[0_0_15px_rgba(121,40,202,0.2)]'
                      : 'bg-slate-900 border-slate-800 text-slate-400 hover:bg-slate-800'
                  }`}
                >
                  <Globe className="w-4 h-4" />
                  <span>OpenAI Cloud</span>
                </button>
              </div>
            </div>

            {/* Ollama Config fields */}
            {provider === 'ollama' && (
              <div className="space-y-4 pt-2">
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">
                    Ollama Base URL
                  </label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    placeholder="http://localhost:11434"
                    className="w-full rounded-xl bg-slate-900 border border-slate-700 p-3 text-xs text-white font-mono focus:outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">
                    Ollama Model Identifier
                  </label>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="qwen2.5-coder:32b"
                    className="w-full rounded-xl bg-slate-900 border border-slate-700 p-3 text-xs text-white font-mono focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>
            )}

            {/* OpenAI Config fields */}
            {provider === 'openai' && (
              <div className="space-y-4 pt-2">
                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-..."
                    className="w-full rounded-xl bg-slate-900 border border-slate-700 p-3 text-xs text-white font-mono focus:outline-none focus:border-purple-400"
                  />
                </div>

                <div>
                  <label className="text-xs font-semibold text-slate-300 mb-1 block">
                    Model Name
                  </label>
                  <input
                    type="text"
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    placeholder="gpt-4o-mini"
                    className="w-full rounded-xl bg-slate-900 border border-slate-700 p-3 text-xs text-white font-mono focus:outline-none focus:border-purple-400"
                  />
                </div>
              </div>
            )}

            {/* Save Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-400 hover:text-white transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-6 py-2.5 rounded-xl text-xs font-bold bg-cyan-500 hover:bg-cyan-400 text-black flex items-center gap-2 transition-all shadow-md"
              >
                <Save className="w-4 h-4" />
                <span>Save Configuration</span>
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
