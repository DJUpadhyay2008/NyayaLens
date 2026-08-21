import React from 'react';
import { ExternalLink, BookOpen, Calendar, MapPin, Scale, ChevronRight } from 'lucide-react';

export const ResultCard = ({ result, onSelectCase }) => {
  const formatScore = (score) => Math.round(score * 100);

  const getScoreBadgeClass = (score) => {
    const pct = formatScore(score);
    if (pct >= 85) return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
    if (pct >= 60) return 'bg-amber-500/20 text-amber-300 border border-amber-500/40';
    return 'bg-slate-700/50 text-slate-300 border border-slate-600';
  };

  return (
    <div className="bg-judicial-800/90 border border-judicial-700/80 rounded-2xl p-6 shadow-xl hover:border-amber-500/40 transition-all space-y-4 group">
      
      {/* Header Row: Title & Relevance Badge */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-judicial-700/60 pb-3">
        <div className="space-y-1">
          <div className="flex items-center space-x-2 text-xs font-medium text-slate-400">
            <Scale className="w-3.5 h-3.5 text-amber-400" />
            <span>Supreme Court of India</span>
            <span>•</span>
            <span className="text-amber-300 font-mono">{result.citation || 'Commercial Judgment'}</span>
          </div>

          <h3 
            onClick={() => onSelectCase(result.case_id)}
            className="text-lg sm:text-xl font-bold text-amber-300 hover:text-amber-200 font-serif cursor-pointer transition-colors leading-snug group-hover:underline"
          >
            {result.case_name}
          </h3>
        </div>

        {/* Relevance Percentage Badge */}
        <div className="shrink-0 flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${getScoreBadgeClass(result.score)}`}>
            {formatScore(result.score)}% Relevance
          </span>
        </div>
      </div>

      {/* Case Metadata Badges */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 font-medium">
        <div className="flex items-center space-x-1.5 bg-judicial-900/90 px-2.5 py-1 rounded-md border border-judicial-700">
          <Calendar className="w-3.5 h-3.5 text-slate-400" />
          <span>{result.decision_date || 'Decision Date N/A'}</span>
        </div>

        <div className="flex items-center space-x-1.5 bg-judicial-900/90 px-2.5 py-1 rounded-md border border-judicial-700">
          <MapPin className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-semibold text-amber-300">{result.paragraph || 'Paragraph Reference'}</span>
          <span className="text-slate-400">(Page {result.page || 1})</span>
        </div>

        {result.bench && (
          <div className="hidden sm:flex items-center space-x-1.5 bg-judicial-900/90 px-2.5 py-1 rounded-md border border-judicial-700 truncate max-w-xs text-slate-400">
            <span>Bench: {result.bench}</span>
          </div>
        )}
      </div>

      {/* Snippet / Relevant Passage */}
      <div className="bg-judicial-900/90 border border-judicial-700/70 rounded-xl p-4 text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
        <p className="italic text-slate-200">
          "{result.passage}"
        </p>
      </div>

      {/* Bottom Actions Bar */}
      <div className="flex items-center justify-between pt-1 text-xs">
        <button
          onClick={() => onSelectCase(result.case_id)}
          className="inline-flex items-center space-x-1.5 font-medium text-amber-400 hover:text-amber-300 transition-colors cursor-pointer group-hover:translate-x-0.5 transform"
        >
          <BookOpen className="w-4 h-4 text-amber-400" />
          <span>View Full Case & Chunks</span>
          <ChevronRight className="w-4 h-4" />
        </button>

        {result.pdf_url && (
          <a
            href={result.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-1 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span>AWS Open Data PDF</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>

    </div>
  );
};
