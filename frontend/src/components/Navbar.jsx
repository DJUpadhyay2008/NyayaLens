import React from 'react';
import { Scale, Landmark, Database } from 'lucide-react';

export const Navbar = ({ stats }) => {
  return (
    <header className="bg-judicial-900 border-b border-judicial-700/80 sticky top-0 z-40 backdrop-blur-md bg-opacity-95 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between min-h-[64px] py-2.5">
          
          {/* Brand Identity */}
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 bg-gradient-to-br from-amber-500/20 to-yellow-600/10 border border-amber-500/30 rounded-xl shadow-inner text-amber-400">
              <Scale className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-black tracking-tight text-white font-sans">
                  Nyaya<span className="text-amber-400">Lens</span>
                </h1>
                <span className="bg-amber-500/15 text-amber-300 border border-amber-500/30 text-xs px-2 py-0.5 rounded font-semibold uppercase tracking-wider">
                  Commercial Courts
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                AI Legal Research Engine • Supreme Court of India Commercial Corpus
              </p>
            </div>
          </div>

          {/* Right Status Badge & Court Info */}
          <div className="hidden md:flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-judicial-800 border border-judicial-700/60 px-3 py-1.5 rounded-lg text-xs text-slate-300">
              <Landmark className="w-4 h-4 text-amber-400" />
              <span>Target: Commercial Judicial Officers</span>
            </div>

            {stats && (
              <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/30 px-3.5 py-1.5 rounded-lg text-xs text-emerald-400 font-medium">
                <Database className="w-3.5 h-3.5" />
                <span>
                  {stats.indexed_cases || 750} Judgments Indexed ({stats.indexed_chunks || 24668} Chunks)
                </span>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};
