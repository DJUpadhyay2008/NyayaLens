import React, { useState } from 'react';
import { Sparkles, Copy, Check, ShieldCheck, Loader2 } from 'lucide-react';
import { generateSearchSummary } from '../services/api';

export const AIBriefCard = ({ query, results }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const handleGenerate = async () => {
    if (!results || results.length === 0) return;
    setLoading(true);
    setIsOpen(true);
    try {
      const res = await generateSearchSummary(query, results);
      setSummary(res.summary);
    } catch (err) {
      console.error("Search AI synthesis error:", err);
      setSummary("### ⚠️ Unable to generate AI Search Synthesis.\nPlease try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (summary) {
      navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="w-full bg-gradient-to-r from-judicial-900 via-judicial-800 to-judicial-900 border border-amber-500/30 rounded-2xl p-5 shadow-xl transition-all">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20">
            <Sparkles className="w-5 h-5 fill-amber-400/20" />
          </div>
          <div>
            <h3 className="text-sm sm:text-base font-bold text-amber-300 font-serif flex items-center space-x-2">
              <span>AI Judicial Executive Synthesis</span>
              <span className="bg-amber-500/15 text-amber-300 text-[10px] px-2 py-0.5 rounded-full border border-amber-500/30 font-mono">
                OpenRouter GLM-5.2
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Synthesize top {results.length} retrieved Supreme Court precedents into a zero-hallucination judicial brief.
            </p>
          </div>
        </div>

        <button
          onClick={isOpen && summary ? () => setIsOpen(!isOpen) : handleGenerate}
          disabled={loading}
          className="flex items-center justify-center space-x-2 bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs shadow-lg transition-all cursor-pointer whitespace-nowrap"
        >
          {loading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Synthesizing Precedents...</span>
            </>
          ) : isOpen && summary ? (
            <span>{isOpen ? "Collapse AI Synthesis" : "View AI Synthesis"}</span>
          ) : (
            <>
              <Sparkles className="w-3.5 h-3.5 fill-slate-950" />
              <span>Generate AI Search Brief</span>
            </>
          )}
        </button>
      </div>

      {/* Expanded AI Synthesis Content */}
      {isOpen && (
        <div className="mt-4 pt-4 border-t border-judicial-700/60 space-y-3 animate-fade-in">
          {loading ? (
            <div className="py-8 text-center space-y-2">
              <Loader2 className="w-8 h-8 text-amber-400 animate-spin mx-auto" />
              <p className="text-xs text-slate-300">
                Running OpenRouter RAG Engine on {results.length} Precedent Chunks...
              </p>
            </div>
          ) : (
            <div className="bg-judicial-950/80 rounded-xl p-4 border border-judicial-700/80 space-y-3">
              <div className="flex items-center justify-between border-b border-judicial-800 pb-2">
                <div className="flex items-center space-x-1.5 text-xs text-emerald-400 font-medium">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Strict Precedent-Anchored Executive Brief</span>
                </div>

                <button
                  onClick={handleCopy}
                  className="flex items-center space-x-1 text-xs text-slate-300 hover:text-white bg-judicial-800 px-2.5 py-1 rounded border border-judicial-700 transition-colors"
                >
                  {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? "Copied" : "Copy Brief"}</span>
                </button>
              </div>

              <div className="text-slate-200 text-xs sm:text-sm leading-relaxed whitespace-pre-line font-sans">
                {summary}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
