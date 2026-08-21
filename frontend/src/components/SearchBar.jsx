import React from 'react';
import { Search, Sparkles, ArrowRight, X } from 'lucide-react';

export const SearchBar = ({ query, setQuery, onSearch, isLoading }) => {
  const exampleQueries = [
    "Cases involving delayed payment and breach of contract",
    "Force majeure in commercial contracts",
    "Damages for breach of commercial agreements",
    "Arbitration agreement enforcement under Section 11"
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-amber-400 transition-colors z-10">
          <Search className="w-5 h-5" />
        </div>
        
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter natural-language legal question, commercial dispute topic, or citation..."
          className="w-full pl-12 pr-36 py-4 bg-judicial-800/90 border border-judicial-700/80 rounded-2xl text-slate-100 placeholder-slate-400 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 shadow-2xl transition-all font-sans"
        />

        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="absolute inset-y-0 right-32 pr-1 flex items-center text-slate-400 hover:text-slate-200 z-10 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        )}

        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="absolute right-2 top-2 bottom-2 px-5 bg-gradient-to-r from-amber-500 to-yellow-600 hover:from-amber-400 hover:to-yellow-500 text-judicial-900 font-semibold rounded-xl flex items-center space-x-2 transition-all shadow-md disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer z-10 text-sm"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-judicial-900 border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <span>Search</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>

      {/* Suggested Search Queries */}
      <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
        <span className="flex items-center space-x-1 text-slate-400 font-medium mr-1">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Suggested Queries:</span>
        </span>
        {exampleQueries.map((ex, i) => (
          <button
            key={i}
            type="button"
            onClick={() => {
              setQuery(ex);
              onSearch(ex);
            }}
            className="bg-judicial-800/90 hover:bg-judicial-700 border border-judicial-700 hover:border-amber-500/50 text-slate-300 hover:text-amber-300 px-3 py-1.5 rounded-lg transition-all text-left shadow-sm cursor-pointer"
          >
            "{ex}"
          </button>
        ))}
      </div>
    </div>
  );
};
