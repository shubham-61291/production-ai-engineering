import React, { useState } from 'react';
import { ApiClient } from '../api';

interface DocumentUploadProps {
  sessionId: string;
  onUploadComplete: (filename: string) => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ sessionId, onUploadComplete }) => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await ApiClient.upload(file, sessionId);
      onUploadComplete(file.name);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="p-4 border border-gray-700 rounded-lg bg-gray-800/40">
      <h3 className="text-sm font-semibold text-gray-300 mb-2">Upload RAG Document</h3>
      <input
        type="file"
        accept=".pdf,.docx,.txt,.md"
        onChange={handleUpload}
        disabled={uploading}
        className="block w-full text-xs text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
      />
      {uploading && <div className="mt-2 text-xs text-blue-400">Embedding and indexing document...</div>}
      {error && <div className="mt-2 text-xs text-red-400">{error}</div>}
    </div>
  );
};

export default DocumentUpload;
