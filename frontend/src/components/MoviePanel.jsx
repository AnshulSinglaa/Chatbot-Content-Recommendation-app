import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Star, Clapperboard, Send } from 'lucide-react';

const MoviePanel = ({ movie, onClose, onFindSimilar }) => {
  return (
    <AnimatePresence>
      <motion.div 
        initial={{ x: 300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 300, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="w-[300px] h-screen bg-brand-card border-l border-brand-border flex flex-col shrink-0 overflow-y-auto"
      >
        {movie ? (
          <div className="flex flex-col p-6 h-full relative">
            <button onClick={onClose} className="absolute top-6 right-6 text-brand-muted hover:text-white transition-colors bg-brand-primary p-1.5 rounded-md border border-brand-border z-10">
              <X size={16} />
            </button>
            
            <div className="mt-8 mb-6">
              <h2 className="text-2xl font-bold text-white mb-3 tracking-tight pr-8">{movie.title}</h2>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 bg-brand-primary px-2 py-1 rounded-md text-sm font-medium text-amber-400 shrink-0 border border-brand-border/50">
                  <Star size={14} className="fill-amber-400" />
                  {movie.rating ? movie.rating.toFixed(1) : 'N/A'}
                </div>
              </div>
            </div>

            {movie.genres && (
              <div className="flex flex-wrap gap-2 mb-6">
                {movie.genres.split('|').map((g, i) => (
                  <span key={i} className="text-[11px] bg-brand-primary text-brand-text px-2.5 py-1 rounded-full border border-brand-border">
                    {g}
                  </span>
                ))}
              </div>
            )}

            <div className="mb-6">
              <h3 className="text-[11px] font-bold text-brand-placeholder mb-2 uppercase tracking-wider">Overview</h3>
              <p className="text-sm text-brand-muted leading-relaxed">
                {movie.overview || "No overview available for this title."}
              </p>
            </div>

            <div className="mb-8">
              <h3 className="text-[11px] font-bold text-brand-placeholder mb-2 uppercase tracking-wider">Why we recommend it</h3>
              <p className="text-sm text-brand-text bg-brand-primary p-3.5 rounded-xl border border-brand-border italic leading-relaxed shadow-inner shadow-black/20">
                "{movie.explanation}"
              </p>
            </div>

            <div className="mt-auto pt-6">
              <button 
                onClick={() => {
                   onFindSimilar(`I want more movies similar to ${movie.title}`);
                   onClose();
                }}
                className="w-full flex items-center justify-center gap-2 bg-brand-accent hover:bg-brand-accent-hover text-white py-3.5 rounded-xl transition-colors text-sm font-medium shadow-lg shadow-brand-accent/20"
              >
                <Send size={16} />
                Find Similar Movies
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-6 h-full text-center">
             <div className="w-16 h-16 bg-brand-primary rounded-full flex items-center justify-center text-brand-accent mb-6 border border-brand-border shadow-md">
               <Clapperboard size={24} />
             </div>
             <h3 className="text-lg font-bold text-white mb-2 tracking-tight">Movie Details</h3>
             <p className="text-sm text-brand-muted mb-8 max-w-[200px] mx-auto leading-relaxed">
               Click "Tell me more" on any recommendation to see the full plot and details here.
             </p>
             
             <div className="w-full bg-brand-primary p-4 rounded-xl border border-brand-border text-left shadow-inner shadow-black/20">
               <h4 className="text-[10px] font-bold text-brand-placeholder uppercase tracking-wider mb-3">Database Stats</h4>
               <div className="flex justify-between items-center mb-2 pb-2 border-b border-brand-border/50 text-sm">
                 <span className="text-brand-muted">Total Movies</span>
                 <span className="text-white font-medium">9,800+</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-brand-muted">AI Model</span>
                 <span className="text-white font-medium">Llama 3.1</span>
               </div>
             </div>
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default MoviePanel;
