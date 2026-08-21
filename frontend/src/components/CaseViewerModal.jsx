import React, { useState, useEffect } from 'react';
import { X, Calendar, ExternalLink, Scale, Loader2 } from 'lucide-react';
import { getCaseDetails } from '../services/api';

export const CaseViewerModal = ({ caseId, onClose }) => {
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('full_text');

  useEffect(() => {
    if (caseId) {
      setLoading(true);
      setError(null);
      getCaseDetails(caseId)
        .then(data => {
          setCaseData(data);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error fetching case details:", err);
          setError("Failed to load full judgment details.");
          setLoading(false);
        });
    }
  }, [caseId]);

  if (!caseId) return null;

  const caseName = caseData?.title || "Commercial Law Judgment";
  const citation = caseData?.citation || "Supreme Court Precedent";
  const decisionDate = caseData?.decision_date || caseData?.year || "Date N/A";
  const bench = caseData?.judges || "";
  const pdfUrl = caseData?.source_url || "";
  const fullText = caseData?.raw_text || "Full document text is unavailable.";
  const chunks = caseData?.chunks || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-judicial-900 border border-judicial-700 rounded-3xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden text-slate-100">
        
        {/* Modal Top Header */}
        <div className="p-6 border-b border-judicial-700/80 flex items-start justify-between bg-judicial-800/80">
          <div className="space-y-1 pr-6">
            <div className="flex items-center space-x-2 text-xs font-medium text-slate-400">
              <Scale className="w-4 h-4 text-amber-400" />
              <span>Official Supreme Court Judgment</span>
              <span>•</span>
              <span className="text-amber-300 font-mono">{citation}</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-amber-300 font-serif leading-snug">
              {loading ? "Loading Judgment Document..." : caseName}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white hover:bg-judicial-700 rounded-full transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Loading / Error States */}
        {loading && (
          <div className="py-24 text-center space-y-3">
            <Loader2 className="w-10 h-10 text-amber-400 animate-spin mx-auto" />
            <p className="text-slate-300 text-sm font-medium">Retrieving Full Judgment Document & Paragraph Vectors...</p>
          </div>
        )}

        {error && (
          <div className="py-16 text-center text-red-400 space-y-2">
            <p className="font-bold">{error}</p>
            <button onClick={onClose} className="px-4 py-2 bg-judicial-800 text-white rounded-xl text-xs">Close Viewer</button>
          </div>
        )}

        {!loading && !error && caseData && (
          <>
            {/* Metadata Bar */}
            <div className="bg-judicial-950 border-b border-judicial-700/60 px-6 py-3 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-300">
              <div className="flex flex-wrap items-center gap-4">
                <span className="flex items-center space-x-1 font-medium">
                  <Calendar className="w-3.5 h-3.5 text-amber-400" />
                  <span>Date: {decisionDate}</span>
                </span>
                {bench && (
                  <span className="font-medium text-slate-300">
                    Bench: {bench}
                  </span>
                )}
                <span className="bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-0.5 rounded text-emerald-300 font-semibold">
                  {chunks.length} Chunks Indexed
                </span>
              </div>

              {pdfUrl && (
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-amber-400 hover:underline font-bold"
                >
                  <span>Download S3 PDF</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-judicial-700/60 px-6 bg-judicial-900/50">
              <button
                onClick={() => setActiveTab('full_text')}
                className={`px-4 py-3 text-xs font-bold border-b-2 transition-colors cursor-pointer ${
                  activeTab === 'full_text'
                    ? 'border-amber-400 text-amber-300'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Full Judgment Text
              </button>
              <button
                onClick={() => setActiveTab('chunks')}
                className={`px-4 py-3 text-xs font-bold border-b-2 transition-colors cursor-pointer ${
                  activeTab === 'chunks'
                    ? 'border-amber-400 text-amber-300'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                Paragraph Chunks Breakdown ({chunks.length})
              </button>
            </div>

            {/* Modal Body Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 font-sans text-sm leading-relaxed text-slate-200 bg-judicial-900">
              {activeTab === 'full_text' ? (
                <div className="prose prose-invert max-w-none space-y-4">
                  <div className="bg-judicial-950 border border-judicial-700 rounded-xl p-4 text-xs font-mono text-slate-400">
                    <p>SUPREME COURT OF INDIA</p>
                    <p className="font-bold text-amber-300">{caseName}</p>
                    <p>Citation: {citation}</p>
                  </div>
                  <div className="whitespace-pre-line text-slate-200 text-sm leading-relaxed font-serif">
                    {fullText}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {chunks.map((chunk, idx) => (
                    <div key={idx} className="bg-judicial-950 border border-judicial-700/70 rounded-xl p-4 space-y-2">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-400 border-b border-judicial-700/60 pb-2">
                        <span className="text-amber-300 font-bold">{chunk.paragraph_reference || `Paragraph ${idx + 1}`}</span>
                        <span>Page {chunk.page_number || 1} • Chunk #{idx + 1}</span>
                      </div>
                      <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-sans">
                        {chunk.text}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {/* Modal Footer */}
        <div className="p-4 border-t border-judicial-700/80 bg-judicial-950 flex items-center justify-between text-xs text-slate-400">
          <span>NyayaLens Judicial Research Portal</span>
          <button
            onClick={onClose}
            className="px-5 py-2 bg-judicial-800 hover:bg-judicial-700 text-white font-bold rounded-xl shadow transition-all cursor-pointer"
          >
            Close Viewer
          </button>
        </div>

      </div>
    </div>
  );
};
