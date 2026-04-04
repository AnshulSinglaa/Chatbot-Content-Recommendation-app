import React from 'react';
import { motion } from 'framer-motion';
import { Clapperboard } from 'lucide-react';

const chips = [
  "Something light and funny for a tired evening",
  "A mind-bending thriller like Inception",
  "Feel-good movies to watch with family",
  "Dark and intense drama, highly rated"
];

const SuggestionChips = ({ onSelect }) => {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8">
      <div className="bg-brand-card p-6 rounded-full text-brand-accent mb-6 shadow-xl shadow-brand-accent/5">
        <Clapperboard size={48} strokeWidth={1.5} />
      </div>
      <h2 className="text-2xl font-bold text-white mb-2 text-center">What are you in the mood for tonight?</h2>
      <p className="text-brand-muted mb-10 text-center">Try asking me something like...</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
        {chips.map((chip, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelect(chip)}
            className="p-4 rounded-xl glass-panel text-sm text-left text-brand-muted hover:text-white transition-colors"
          >
            "{chip}"
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default SuggestionChips;
