import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import MagnetarBackground from './components/MagnetarBackground';
import Header from './components/Header';
import BuilderConsole from './components/BuilderConsole';
import LiveBuildTracker from './components/LiveBuildTracker';
import DownloadSection from './components/DownloadSection';
import SettingsModal from './components/SettingsModal';

export default function App() {
  const [health, setHealth] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [currentRunId, setCurrentRunId] = useState(null);
  const [buildStatus, setBuildStatus] = useState('');
  const [logs, setLogs] = useState('');
  const [mainPy, setMainPy] = useState('');
  const [requirementsTxt, setRequirementsTxt] = useState('');
  const [exeReady, setExeReady] = useState(false);
  const [isBuilding, setIsBuilding] = useState(false);

  const [settings, setSettings] = useState({
    provider: 'ollama',
    base_url: 'http://localhost:11434',
    model: 'qwen2.5-coder:32b',
    api_key: ''
  });

  // Fetch API health check on load
  const fetchHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
        if (data.default_model) {
          setSettings(prev => ({ ...prev, model: data.default_model, base_url: data.ollama_url }));
        }
      }
    } catch (err) {
      console.warn('Health check failed:', err);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Handle WebSocket updates for current run
  useEffect(() => {
    if (!currentRunId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/build/${currentRunId}`;
    let socket = new WebSocket(wsUrl);

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status) setBuildStatus(data.status);
        if (data.logs) setLogs(data.logs);
        if (data.main_py) setMainPy(data.main_py);
        if (data.requirements_txt) setRequirementsTxt(data.requirements_txt);
        if (data.exe_ready !== undefined) setExeReady(data.exe_ready);

        if (data.status?.includes('DONE') || data.status?.includes('ERROR') || data.exe_ready) {
          setIsBuilding(false);
        }
      } catch (err) {
        console.error('WebSocket parse error:', err);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    return () => {
      socket.close();
    };
  }, [currentRunId]);

  // Start Build Handler
  const handleStartBuild = async (requirements) => {
    setIsBuilding(true);
    setBuildStatus('Initiating agent pipeline...');
    setLogs('Connecting to Qwen2.5-Coder ReAct engine...');
    setMainPy('');
    setRequirementsTxt('');
    setExeReady(false);

    try {
      const res = await fetch('/api/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          requirements,
          provider: settings.provider,
          model: settings.model,
          base_url: settings.base_url,
          api_key: settings.api_key
        })
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      setCurrentRunId(data.run_id);
    } catch (err) {
      setBuildStatus(`Failed: ${err.message}`);
      setLogs(prev => prev + `\n[ERROR] ${err.message}`);
      setIsBuilding(false);
    }
  };

  return (
    <main className="relative min-h-screen bg-black text-white overflow-x-hidden font-sans selection:bg-cyan-500 selection:text-black">
      {/* 3D Magnetar Star Canvas Background */}
      <MagnetarBackground />

      {/* Header */}
      <Header 
        health={health} 
        onOpenSettings={() => setIsSettingsOpen(true)} 
      />

      {/* Main Content Area */}
      <div className="relative z-10 px-4 md:px-10 pt-8 pb-16 min-h-[calc(100vh-140px)]">
        {/* Hero Section */}
        <section className="text-center max-w-3xl mx-auto mb-8 pt-4">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            className="text-4xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-cyan-300 via-purple-400 to-fuchsia-500 bg-clip-text text-transparent"
          >
            Harnessing AI Power
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1.2, delay: 0.2 }}
            className="mt-3 text-lg md:text-xl text-white font-bold leading-relaxed tracking-wide"
          >
            Enterprise Grade AI Integration & Executable Compiler
          </motion.p>
        </section>

        {/* Builder Console Input */}
        <BuilderConsole 
          onStartBuild={handleStartBuild} 
          isBuilding={isBuilding} 
        />

        {/* Live Build Tracker & Logs */}
        <LiveBuildTracker
          status={buildStatus}
          logs={logs}
          mainPy={mainPy}
          requirementsTxt={requirementsTxt}
          isBuilding={isBuilding}
          exeReady={exeReady}
        />

        {/* Download Section */}
        <DownloadSection 
          runId={currentRunId} 
          exeReady={exeReady} 
        />
      </div>

      {/* Settings Modal */}
      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        onSaveSettings={(newSettings) => setSettings(newSettings)}
      />

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-8 text-center text-xs md:text-sm text-slate-400 bg-black/80 backdrop-blur-md">
        © {new Date().getFullYear()} Magnetar Labs — Engineering the Path to Singularity. All rights reserved.
      </footer>
    </main>
  );
}
