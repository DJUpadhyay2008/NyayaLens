import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SearchBar } from './components/SearchBar';
import { FilterPanel } from './components/FilterPanel';
import { ResultCard } from './components/ResultCard';
import { CaseViewerModal } from './components/CaseViewerModal';
import { searchCorpus, getHealthStatus } from './services/api';
import { ShieldAlert, Scale } from 'lucide-react';

export function App() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({ court: 'All', year: 'All', document_type: 'All' });
  const [results, setResults] = useState([]);
  const [searchMeta, setSearchMeta] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedCaseId, setSelectedCaseId] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    getHealthStatus()
      .then(data => setStats(data))
      .catch(err => console.warn("Backend connection issue:", err));
  }, []);

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setHasSearched(true);
    setErrorMessage(null);

    try {
      const data = await searchCorpus(searchQuery, filters);
      setResults(data.results || []);
      setSearchMeta(data);
    } catch (err) {
      console.error("Search API Error:", err);
      setErrorMessage("Unable to connect to legal search backend server.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetFilters = () => {
    setFilters({ court: 'All', year: 'All', document_type: 'All' });
    if (query.trim()) {
      handleSearch(query);
    }
  };

  return (
    <div className="min-h-screen bg-[#080D1A] text-slate-100 flex flex-col font-sans">
      
      {/* Top Judicial Navbar */}
      <Navbar stats={stats} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Search Hero Section */}
        <section className="text-center space-y-6 max-w-4xl mx-auto pt-4">
          <div className="inline-flex items-center space-x-2 bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs px-3.5 py-1.5 rounded-full font-medium shadow-inner">
            <Scale className="w-4 h-4 text-amber-400" />
            <span>NyayaLens • AI Legal Research Engine</span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white font-serif leading-tight">
            Precision Hybrid Retrieval for <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-amber-300 via-yellow-400 to-amber-500 bg-clip-text text-transparent">
              Indian Commercial Court Judgments
            </span>
          </h2>

          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            NyayaLens combines hybrid semantic vector retrieval and exact keyword search over official Supreme Court of India commercial judgments. Fast, accurate, and citation-backed.
          </p>

          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
            isLoading={loading}
          />
        </section>

        {/* Filter Toolbar */}
        <section className="max-w-4xl mx-auto">
          <FilterPanel
            filters={filters}
            setFilters={setFilters}
            onReset={handleResetFilters}
          />
        </section>

        {/* Search Results Display Area */}
        <section className="max-w-5xl mx-auto space-y-6 pt-4">
          
          {loading && (
            <div className="py-16 text-center space-y-4">
              <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto shadow-lg" />
              <div className="space-y-1">
                <p className="text-slate-200 font-semibold text-base font-serif">
                  Searching Indian Legal Corpus & Computing Dense Embeddings...
                </p>
                <p className="text-slate-400 text-xs">
                  Running PostgreSQL Full-Text Search + pgvector Cosine Distance Reranking
                </p>
              </div>
            </div>
          )}

          {!loading && hasSearched && (
            <>
              {/* Search Result Summary Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-judicial-700/60 pb-3">
                <div className="flex items-center space-x-2 text-sm text-slate-300">
                  <span className="font-semibold text-white">Results for:</span>
                  <span className="italic text-amber-300 font-serif">"{searchMeta?.query}"</span>
                  <span className="bg-judicial-800 text-slate-400 text-xs px-2.5 py-0.5 rounded-full border border-judicial-700">
                    {searchMeta?.total_results || 0} Matches
                  </span>
                </div>

                {searchMeta?.expanded_terms?.length > 0 && (
                  <div className="flex items-center space-x-1.5 text-xs text-slate-400">
                    <span>Key Terms:</span>
                    <div className="flex space-x-1">
                      {searchMeta.expanded_terms.map((t, idx) => (
                        <span key={idx} className="bg-judicial-800 text-amber-400 px-2 py-0.5 rounded border border-judicial-700">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Hallucination Protection Notice / Empty Results */}
              {(results.length === 0 || searchMeta?.message) ? (
                <div className="bg-judicial-800/80 border border-amber-500/30 rounded-2xl p-8 text-center space-y-4 shadow-xl my-8">
                  <div className="p-3 bg-amber-500/10 text-amber-400 rounded-full w-fit mx-auto border border-amber-500/20">
                    <ShieldAlert className="w-8 h-8" />
                  </div>
                  <div className="space-y-2 max-w-md mx-auto">
                    <h3 className="text-lg font-bold text-amber-300 font-serif">
                      Insufficient Evidence Found
                    </h3>
                    <p className="text-slate-300 text-sm font-medium">
                      {searchMeta?.message || "Insufficient evidence found in the current legal corpus."}
                    </p>
                    <p className="text-slate-400 text-xs leading-relaxed pt-2 border-t border-judicial-700">
                      NyayaLens strictly retrieves verified passages from indexed Supreme Court judgments without generating hallucinated legal claims. Try expanding your search terms.
                    </p>
                  </div>
                </div>
              ) : (
                /* Results List */
                <div className="space-y-5">
                  {results.map((res, index) => (
                    <ResultCard
                      key={index}
                      result={res}
                      onSelectCase={setSelectedCaseId}
                    />
                  ))}
                </div>
              )}
            </>
          )}

          {!hasSearched && !loading && (
            <div className="bg-judicial-800/40 border border-judicial-700/40 rounded-2xl p-10 text-center space-y-4 max-w-2xl mx-auto my-6">
              <Scale className="w-12 h-12 text-amber-400/60 mx-auto" />
              <div className="space-y-2">
                <h3 className="text-lg font-bold text-slate-200 font-serif">
                  Ready for Judicial Legal Queries
                </h3>
                <p className="text-slate-400 text-xs leading-relaxed">
                  Select a suggested query above or type a commercial law question to search through indexed Supreme Court of India precedents.
                </p>
              </div>
            </div>
          )}

        </section>

      </main>

      {/* Footer */}
      <footer className="bg-judicial-900 border-t border-judicial-700/80 py-6 text-center text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p>© 2026 NyayaLens • Built for Indian Commercial Courts</p>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>AWS Supreme Court Judgments Corpus</span>
            <span>•</span>
            <span>PostgreSQL + pgvector Hybrid Engine</span>
          </div>
        </div>
      </footer>

      {/* Case Viewer Modal */}
      {selectedCaseId && (
        <CaseViewerModal
          caseId={selectedCaseId}
          onClose={() => setSelectedCaseId(null)}
        />
      )}

    </div>
  );
}

export default App;
