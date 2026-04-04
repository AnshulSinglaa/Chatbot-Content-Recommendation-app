import React from 'react';
import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

const MovieCard = ({ movie, onSelect }) => {
  const genres = movie.genres ? movie.genres.split('|').slice(0, 3) : [];
  
  return (
    <div className="bg-brand-primary border border-brand-border rounded-xl p-5 min-w-[280px] max-w-[300px] flex-shrink-0 flex flex-col justify-between h-[220px]">
      <div>
        <div className="flex justify-between items-start mb-2">
          <h4 className="text-white font-bold text-[15px] leading-tight pr-2 line-clamp-2">{movie.title}</h4>
          <div className="flex items-center gap-1 bg-brand-card px-2 py-1 rounded text-xs font-medium text-amber-400 shrink-0 border border-brand-border/50">
            <Star size={12} className="fill-amber-400" />
            {movie.rating ? movie.rating.toFixed(1) : 'N/A'}
          </div>
        </div>
        
        <div className="flex flex-wrap gap-1.5 mb-3">
          {genres.map((g, i) => (
             <span key={i} className="text-[10px] bg-brand-card text-brand-muted px-2 py-0.5 rounded-full border border-brand-border/50">
               {g}
             </span>
          ))}
        </div>
        
        <p className="text-brand-muted text-xs line-clamp-3 mb-4 leading-relaxed">
          {movie.explanation}
        </p>
      </div>
      
      <button 
        onClick={() => onSelect(movie)}
        className="text-xs font-medium text-white bg-white/5 hover:bg-white/10 transition-colors py-2 rounded-lg w-full mt-auto border border-brand-border/50"
      >
        Tell me more
      </button>
    </div>
  );
};

export default MovieCard;
