import React from 'react';

interface AuditProgressProps {
  jobId: string;
  status: any;
}

const AuditProgress: React.FC<AuditProgressProps> = ({ jobId, status }) => {
  if (!status) return null;

  const statusMap: Record<string, { label: string; color: string }> = {
    pending: { label: 'Queued in background...', color: 'text-yellow-400' },
    running: { label: 'LangGraph multi-agent reflexion running...', color: 'text-blue-400 animate-pulse' },
    completed: { label: 'Audit Complete', color: 'text-green-400' },
    failed: { label: 'Audit Failed', color: 'text-red-400' },
  };
  const info = statusMap[status.status] || { label: status.status, color: 'text-gray-400' };

  return (
    <div className="mt-4 p-4 border border-gray-700 rounded-lg bg-gray-800/80">
      <div className="flex items-center gap-2">
        <span className="font-semibold text-sm">Job ID:</span>
        <span className="text-xs font-mono text-gray-400 bg-gray-900 px-2 py-1 rounded">{jobId}</span>
      </div>
      <div className={`mt-2 font-medium text-sm ${info.color}`}>
        Status: {info.label}
      </div>
      {status.progress && <div className="text-xs text-gray-400 mt-1">{status.progress}</div>}
      {status.error && <div className="text-xs text-red-400 mt-1">Error: {status.error}</div>}
    </div>
  );
};

export default AuditProgress;
