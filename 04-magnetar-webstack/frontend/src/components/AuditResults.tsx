import React from 'react';

interface AuditResultsProps {
  report: any;
  onDownload: () => void;
}

const AuditResults: React.FC<AuditResultsProps> = ({ report, onDownload }) => {
  if (!report) return null;

  const { executive_summary, overall_compliance_score, flagged_clauses } = report;

  return (
    <div className="mt-6 p-5 border border-gray-700 rounded-lg bg-gray-800/80 shadow-xl space-y-6">
      <div className="flex justify-between items-center border-b border-gray-700 pb-4">
        <h3 className="text-xl font-bold text-white">Audit Results & Summary</h3>
        <button
          onClick={onDownload}
          className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-sm font-medium text-white transition-colors flex items-center gap-2"
        >
          📄 Download PDF Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 bg-gray-900/60 rounded-lg border border-gray-700 text-center flex flex-col justify-center">
          <span className="text-xs text-gray-400 font-semibold uppercase">Compliance Score</span>
          <span className={`text-3xl font-extrabold mt-1 ${
            overall_compliance_score >= 80 ? 'text-green-400' :
            overall_compliance_score >= 50 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {overall_compliance_score}/100
          </span>
        </div>
        <div className="md:col-span-3 p-4 bg-gray-900/60 rounded-lg border border-gray-700">
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Executive Summary</h4>
          <p className="text-sm text-gray-200 leading-relaxed">{executive_summary}</p>
        </div>
      </div>

      {flagged_clauses && flagged_clauses.length > 0 && (
        <div>
          <h4 className="text-md font-semibold text-white mb-3">Flagged Clauses ({flagged_clauses.length})</h4>
          <div className="space-y-3">
            {flagged_clauses.map((flag: any, idx: number) => {
              const risk = (flag.risk_level || 'Medium').toLowerCase();
              const borderColor = risk === 'critical' ? 'border-red-500 bg-red-950/20' :
                                  risk === 'high' ? 'border-orange-500 bg-orange-950/20' :
                                  risk === 'medium' ? 'border-yellow-500 bg-yellow-950/20' : 'border-blue-500 bg-blue-950/20';
              const badgeColor = risk === 'critical' ? 'bg-red-900/60 text-red-300' :
                                 risk === 'high' ? 'bg-orange-900/60 text-orange-300' :
                                 risk === 'medium' ? 'bg-yellow-900/60 text-yellow-300' : 'bg-blue-900/60 text-blue-300';
              return (
                <div key={idx} className={`border-l-4 ${borderColor} p-4 rounded-r-lg bg-gray-900/40 border-y border-r border-gray-700/50 space-y-2`}>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${badgeColor}`}>
                      {(flag.risk_level || 'Medium').toUpperCase()} RISK
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">
                    <span className="font-semibold text-gray-200">Clause:</span> "{flag.offending_clause}"
                  </p>
                  <p className="text-xs text-gray-400">
                    <span className="font-semibold text-gray-300">Explanation:</span> {flag.violation_explanation}
                  </p>
                  <p className="text-xs text-green-400 bg-green-950/40 p-2 rounded border border-green-800/40">
                    <span className="font-semibold">Suggested Fix:</span> {flag.suggested_rewrite}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditResults;
