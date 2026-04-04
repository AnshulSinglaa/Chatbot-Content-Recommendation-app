import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Toast = ({ message, type = 'success', onClose }) => {
  useEffect(() => {
    if (message) {
      const timer = setTimeout(onClose, 3000);
      return () => clearTimeout(timer);
    }
  }, [message, onClose]);

  return (
    <AnimatePresence>
      {message && (
        <motion.div
           initial={{ x: 100, opacity: 0 }}
           animate={{ x: 0, opacity: 1 }}
           exit={{ x: 100, opacity: 0 }}
           className={`fixed bottom-6 right-6 px-6 py-4 bg-brand-card text-brand-text rounded-lg shadow-2xl border-l-[4px] border border-brand-border z-50 flex items-center gap-3 ${type === 'success' ? 'border-l-brand-success' : 'border-l-brand-accent'}`}
        >
          <span className="text-sm font-medium">{message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Toast;
