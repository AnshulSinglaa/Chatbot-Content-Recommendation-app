import React, { useState, useRef, useEffect } from 'react';
import { Trash2, Send, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { fetchApi } from '../utils/api';
import Sidebar from './Sidebar';
import MoviePanel from './MoviePanel';
import MessageBubble from './MessageBubble';
import SuggestionChips from './SuggestionChips';
import Toast from './Toast';

const Chat = ({ navigate }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [toast, setToast] = useState({ msg: '', type: 'success' });
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const showToast = (msg, type = 'success') => setToast({ msg, type });

  const handleSend = async (text) => {
    if (!text.trim()) return;
    
    // Add user message to UI immediately
    const newMessages = [...messages, { sender: 'user', text }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      const data = await fetchApi('/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text, use_history: true })
      });
      
      setMessages([...newMessages, { 
        sender: 'ai', 
        text: data.message, 
        recommendations: data.recommendations || []
      }]);
    } catch (err) {
      showToast(err.message || 'Failed to get recommendation', 'error');
      setMessages([...newMessages, { sender: 'ai', text: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = async () => {
    try {
      await fetchApi('/clear', { method: 'POST' });
      setMessages([]);
      setSelectedMovie(null);
      showToast('Conversation cleared');
    } catch (err) {
      showToast('Failed to clear conversation', 'error');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  return (
    <div className="flex h-screen bg-brand-primary overflow-hidden font-sans text-brand-text">
      
      {/* 3 Column Layout */}
      <Sidebar navigate={navigate} />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col relative bg-brand-primary min-w-0 shadow-[-10px_0_30px_-15px_rgba(0,0,0,0.5)] z-10">
        
        {/* Header Bar */}
        <div className="h-16 border-b border-brand-border flex items-center justify-between px-8 py-4 shrink-0 bg-brand-primary/80 backdrop-blur-sm z-20">
          <div className="flex items-center gap-3">
             <h1 className="font-bold text-white tracking-tight">Movies AI</h1>
             <span className="flex h-2 w-2">
               <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-brand-success opacity-75"></span>
               <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-success"></span>
             </span>
             <span className="text-xs font-medium text-brand-success">Online</span>
          </div>
          
          <button 
             onClick={handleClear}
             className="text-brand-muted hover:text-brand-accent transition-colors flex items-center gap-2 text-sm font-medium px-3 py-1.5 rounded-lg hover:bg-brand-accent/10"
             title="Clear conversation"
          >
             <Trash2 size={16} />
             <span className="hidden sm:inline">Clear</span>
          </button>
        </div>

        {/* Scrollable Messages Area */}
        <div className="flex-1 overflow-y-auto w-full custom-scrollbar flex flex-col items-center">
           <div className="w-full max-w-4xl p-6 sm:p-8 flex-1 flex flex-col h-full">
              {messages.length === 0 ? (
                 <SuggestionChips onSelect={handleSend} />
              ) : (
                 <div className="flex flex-col gap-8 pb-4">
                    {messages.map((m, i) => (
                      <MessageBubble 
                        key={i} 
                        message={m} 
                        isAI={m.sender === 'ai'} 
                        onSelectMovie={setSelectedMovie} 
                      />
                    ))}
                    {isLoading && (
                      <div className="self-start flex gap-4 max-w-[85%] mb-4">
                         <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1 bg-brand-secondary text-brand-accent border border-brand-border shadow-sm">
                            <Loader2 size={16} className="animate-spin" />
                         </div>
                         <div className="p-4 bg-brand-card rounded-2xl rounded-tl-sm border border-brand-border shadow-sm flex items-center gap-1.5">
                            <motion.span animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} className="w-1.5 h-1.5 bg-brand-accent rounded-full block"></motion.span>
                            <motion.span animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} className="w-1.5 h-1.5 bg-brand-accent rounded-full block"></motion.span>
                            <motion.span animate={{ y: [0, -3, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} className="w-1.5 h-1.5 bg-brand-accent rounded-full block"></motion.span>
                         </div>
                      </div>
                    )}
                 </div>
              )}
              <div ref={messagesEndRef} />
           </div>
        </div>

        {/* Dynamic Input Area */}
        <div className="w-full bg-brand-primary p-6 pt-2 shrink-0 border-t border-brand-border/30">
           <div className="max-w-4xl mx-auto flex gap-3 relative items-end rounded-2xl bg-brand-card border border-brand-border p-2 shadow-sm focus-within:border-brand-accent/50 focus-within:shadow-md transition-all">
              <textarea 
                 value={input}
                 onChange={(e) => setInput(e.target.value)}
                 onKeyDown={handleKeyDown}
                 placeholder="Describe what you want to watch..."
                 className="flex-1 max-h-32 min-h-[50px] bg-transparent text-white placeholder-brand-placeholder resize-none outline-none py-3 px-4 text-[15px] custom-scrollbar"
                 maxLength={500}
                 rows={1}
              />
              <span className="absolute bottom-4 right-16 text-[10px] text-brand-placeholder pointer-events-none font-medium">
                 {input.length}/500
              </span>
              <button 
                onClick={() => handleSend(input)}
                disabled={!input.trim() || isLoading}
                className="w-[50px] h-[50px] shrink-0 rounded-xl bg-brand-accent hover:bg-brand-accent-hover disabled:bg-brand-secondary disabled:text-brand-placeholder disabled:cursor-not-allowed text-white flex items-center justify-center transition-colors shadow-lg shadow-brand-accent/10 mb-0.5"
              >
                 <Send size={18} className={input.trim() && !isLoading ? 'ml-1' : ''} />
              </button>
           </div>
           <p className="text-center text-[10px] text-brand-placeholder mt-3">
              CineGuide AI can make mistakes. Consider checking important metadata.
           </p>
        </div>
      </div>

      {/* Right Drawer Layout */}
      <MoviePanel 
         movie={selectedMovie} 
         onClose={() => setSelectedMovie(null)} 
         onFindSimilar={(q) => handleSend(q)} 
      />
      
      <Toast message={toast.msg} type={toast.type} onClose={() => setToast({ msg: '' })} />
    </div>
  );
};

export default Chat;
