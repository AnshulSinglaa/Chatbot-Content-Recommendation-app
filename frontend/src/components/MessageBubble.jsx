import React from 'react';
import { Sparkles, User } from 'lucide-react';
import { motion } from 'framer-motion';
import MovieCard from './MovieCard';

const MessageBubble = ({ message, isAI, onSelectMovie }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-4 w-full ${isAI ? 'justify-start' : 'justify-end'}`}
    >
      {isAI && (
        <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1 bg-brand-secondary text-brand-accent shadow-sm border border-brand-border">
          <Sparkles size={16} />
        </div>
      )}
      
      <div className={`flex flex-col ${isAI ? 'max-w-full overflow-hidden' : 'max-w-[70%]'}`}>
        {message.text && (
           <div className={`p-4 text-[15px] leading-relaxed shadow-sm ${
             isAI 
               ? 'bg-brand-card text-brand-text rounded-2xl rounded-tl-sm border border-brand-border w-max max-w-full' 
               : 'bg-brand-accent text-white rounded-2xl rounded-tr-sm self-end'
           }`}>
             {message.text}
           </div>
        )}
        
        {isAI && message.recommendations && message.recommendations.length > 0 && (
          <div className="mt-3 flex gap-4 overflow-x-auto pb-4 pt-1 !scrollbar-track-transparent custom-scrollbar w-full max-w-full pr-10">
            {message.recommendations.map((rec, idx) => (
              <motion.div 
                 key={idx}
                 initial={{ opacity: 0, x: 20 }}
                 animate={{ opacity: 1, x: 0 }}
                 transition={{ delay: 0.1 * idx }}
              >
                  <MovieCard movie={rec} onSelect={onSelectMovie} />
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {!isAI && (
        <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1 bg-brand-accent/20 text-brand-accent border border-brand-accent/30 shadow-sm">
          <User size={16} />
        </div>
      )}
    </motion.div>
  );
};

export default MessageBubble;
