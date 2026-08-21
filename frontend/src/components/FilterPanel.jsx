import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';

export const FilterPanel = ({ filters, setFilters, onReset }) => {
  const years = ['All', '2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015'];
  const docTypes = ['All', 'Judgments', 'Orders', 'Appeals'];

  return (
    <div className="bg-judicial-800/80 border border-judicial-700/70 rounded-2xl p-4 sm:p-5 shadow-xl space-y-3">
      <div className="flex items-center justify-between border-b border-judicial-700/60 pb-2">
        <div className="flex items-center space-x-2 text-amber-400 font-semibold text-sm">
          <Filter className="w-4 h-4" />
          <span>Corpus Refinement Filters</span>
        </div>
        <button
          onClick={onReset}
          className="flex items-center space-x-1 text-xs text-slate-400 hover:text-amber-300 font-medium transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Filters</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-1">
        {/* Court Filter */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-400">Court Jurisdiction</label>
          <select
            value={filters.court}
            onChange={(e) => setFilters({ ...filters, court: e.target.value })}
            className="w-full bg-judicial-900 border border-judicial-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          >
            <option value="All">Supreme Court of India (All Bench)</option>
            <option value="Supreme Court">Commercial Appellate Bench</option>
          </select>
        </div>

        {/* Decision Year Filter */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-400">Decision Year</label>
          <select
            value={filters.year}
            onChange={(e) => setFilters({ ...filters, year: e.target.value })}
            className="w-full bg-judicial-900 border border-judicial-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y === 'All' ? 'All Decision Years (2010 - 2025)' : `Year ${y}`}
              </option>
            ))}
          </select>
        </div>

        {/* Document Type Filter */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-slate-400">Document Classification</label>
          <select
            value={filters.document_type}
            onChange={(e) => setFilters({ ...filters, document_type: e.target.value })}
            className="w-full bg-judicial-900 border border-judicial-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          >
            {docTypes.map((dt) => (
              <option key={dt} value={dt}>
                {dt === 'All' ? 'All Document Types' : dt}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};
