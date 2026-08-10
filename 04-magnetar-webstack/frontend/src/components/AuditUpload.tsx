import React, { useState } from 'react';

interface AuditUploadProps {
  onStartAudit: (file: File | null, text: string) => Promise<void>;
}

const AuditUpload: React.FC<AuditUploadProps> = ({ onStartAudit }) => {
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (file || text.trim()) {
      setLoading(true);
      try {
        await onStartAudit(file, text);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="p-5 border border-gray-700 rounded-lg bg-gray-800/60 shadow-lg">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1.5 text-gray-300">Upload Contract (PDF, DOCX, TXT)</label>
          <input
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-xs text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
          />
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1.5 text-gray-300">Or Paste Contract Text</label>
          <textarea
            rows={5}
            className="w-full p-2.5 rounded bg-gray-700 border border-gray-600 text-white text-sm focus:outline-none focus:border-blue-500"
            placeholder="Paste contract clauses here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={(!file && !text.trim()) || loading}
          className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 font-medium rounded text-sm disabled:opacity-50 transition-colors"
        >
          {loading ? 'Starting Multi-Agent Audit...' : 'Start Compliance Audit'}
        </button>
      </form>
    </div>
  );
};

export default AuditUpload;
