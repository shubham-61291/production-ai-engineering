import React, { useState, useEffect } from 'react';
import Chat from './components/Chat';
import DocumentUpload from './components/DocumentUpload';
import Settings from './components/Settings';
import AuditUpload from './components/AuditUpload';
import AuditProgress from './components/AuditProgress';
import AuditResults from './components/AuditResults';
import { ApiClient, setApiKey } from './api';

const App: React.FC = () => {
  const [apiKey, setApiKeyInput] = useState(localStorage.getItem('apiKey') || '');
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem('sessionId');
    return stored || crypto.randomUUID();
  });
  const [useRag, setUseRag] = useState<boolean>(false);
  const [messages, setMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [temperature, setTemperature] = useState(0.0);
  const [maxTokens, setMaxTokens] = useState(512);
  const [activeTab, setActiveTab] = useState<'chat' | 'audit'>('chat');
  const [auditJobId, setAuditJobId] = useState<string | null>(null);
  const [auditStatus, setAuditStatus] = useState<any>(null);
  const [auditReportData, setAuditReportData] = useState<any>(null);
  const [auditPolling, setAuditPolling] = useState(false);

  useEffect(() => {
    localStorage.setItem('sessionId', sessionId);
    if (apiKey) {
      setApiKey(apiKey);
    }
  }, [sessionId, apiKey]);

  const handleLogin = () => {
    if (apiKey.trim()) {
      setApiKey(apiKey.trim());
      localStorage.setItem('apiKey', apiKey.trim());
    }
  };

  const sendMessage = async (question: string) => {
    setMessages(prev => [...prev, {role: 'user', content: question}]);
    setLoading(true);
    try {
      const response = await ApiClient.ask({
        question,
        use_rag: useRag,
        session_id: sessionId,
        temperature,
        max_tokens: maxTokens,
      });
      setMessages(prev => [...prev, {role: 'assistant', content: response.answer}]);
    } catch (error: any) {
      console.error('Error', error);
      setMessages(prev => [...prev, {role: 'assistant', content: `Error: ${error.response?.data?.detail || error.message}`}]);
    } finally {
      setLoading(false);
    }
  };

  const handleStartAudit = async (file: File | null, text: string) => {
    try {
      const result = await ApiClient.startAudit(file || undefined, text, sessionId);
      setAuditJobId(result.job_id);
      setAuditStatus({ status: 'pending' });
      setAuditReportData(null);
      setAuditPolling(true);
    } catch (error: any) {
      console.error('Failed to start audit', error);
      alert(`Audit start failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (auditPolling && auditJobId) {
      interval = setInterval(async () => {
        try {
          const status = await ApiClient.getAuditStatus(auditJobId);
          setAuditStatus(status);
          if (status.status === 'completed' || status.status === 'failed') {
            setAuditPolling(false);
            if (status.status === 'completed') {
              const reportResult = await ApiClient.getAuditResult(auditJobId);
              setAuditReportData(reportResult.report);
            }
          }
        } catch (e) {
          console.error('Polling error', e);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [auditPolling, auditJobId]);

  const downloadReport = async () => {
    if (!auditJobId) return;
    try {
      const blob = await ApiClient.getAuditReport(auditJobId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_${auditJobId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error('Download failed', e);
    }
  };

  if (!localStorage.getItem('apiKey')) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="bg-gray-800 p-8 rounded-lg shadow-lg max-w-md w-full border border-gray-700">
          <h1 className="text-2xl font-bold mb-4 text-center text-blue-400">Magnetar Webstack</h1>
          <p className="text-gray-400 mb-4 text-center text-sm">Enter your API key to authenticate</p>
          <input
            type="password"
            className="w-full p-2.5 rounded bg-gray-700 border border-gray-600 text-white focus:outline-none focus:border-blue-500"
            placeholder="API Key"
            value={apiKey}
            onChange={(e) => setApiKeyInput(e.target.value)}
          />
          <button onClick={handleLogin} className="mt-4 w-full bg-blue-600 hover:bg-blue-700 py-2.5 rounded font-medium transition-colors">
            Connect
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      <header className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50 backdrop-blur">
        <h1 className="text-xl font-bold tracking-tight text-blue-400">Magnetar Webstack</h1>
        <div className="flex gap-4 items-center">
          <div className="flex gap-2 bg-gray-800 p-1 rounded-lg border border-gray-700">
            <button
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${activeTab === 'chat' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              onClick={() => setActiveTab('chat')}
            >
              Chat
            </button>
            <button
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${activeTab === 'audit' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'}`}
              onClick={() => setActiveTab('audit')}
            >
              Audit
            </button>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
            <input type="checkbox" checked={useRag} onChange={() => setUseRag(!useRag)} className="rounded bg-gray-700 border-gray-600 text-blue-600" />
            RAG Mode
          </label>
          <Settings
            temperature={temperature}
            setTemperature={setTemperature}
            maxTokens={maxTokens}
            setMaxTokens={setMaxTokens}
          />
        </div>
      </header>

      <main className="flex-1 flex flex-col md:flex-row overflow-hidden">
        {activeTab === 'chat' && (
          <>
            <div className="flex-1 p-4 flex flex-col">
              <Chat messages={messages} onSend={sendMessage} loading={loading} />
            </div>
            <aside className="w-full md:w-80 p-4 border-l border-gray-700 bg-gray-800/30 overflow-y-auto">
              <DocumentUpload sessionId={sessionId} onUploadComplete={(filename) => setUploadedFiles(prev => [...prev, filename])} />
              <div className="mt-4">
                <h3 className="text-md font-semibold text-gray-300">Uploaded Files</h3>
                <ul className="list-disc pl-5 mt-2 text-sm text-gray-400 space-y-1">
                  {uploadedFiles.map((f, idx) => <li key={idx} className="truncate">{f}</li>)}
                  {uploadedFiles.length === 0 && <li className="list-none text-gray-500 italic">No files uploaded yet</li>}
                </ul>
              </div>
            </aside>
          </>
        )}

        {activeTab === 'audit' && (
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="max-w-4xl mx-auto">
              <h2 className="text-2xl font-bold mb-2">Legal Compliance Audit</h2>
              <p className="text-gray-400 text-sm mb-6">Upload a contract or paste text to perform an audit against GDPR and EU AI Act using multi-agent reflexion.</p>
              <AuditUpload onStartAudit={handleStartAudit} />
              {auditJobId && (
                <>
                  <AuditProgress jobId={auditJobId} status={auditStatus} />
                  {auditStatus?.status === 'completed' && auditReportData && (
                    <AuditResults report={auditReportData} onDownload={downloadReport} />
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
