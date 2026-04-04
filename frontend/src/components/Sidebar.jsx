import React from 'react';
import { useAuth } from '../context/AuthContext';
import { MessageSquare, Clock, Settings, LogOut } from 'lucide-react';

const Sidebar = ({ navigate }) => {
  const { user, logout } = useAuth();
  
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const seed = user?.email || 'random';
  const avatarUrl = `https://api.dicebear.com/8.x/thumbs/svg?seed=${encodeURIComponent(seed)}`;

  return (
    <div className="hidden md:flex w-[260px] h-screen bg-brand-secondary border-r border-brand-border flex-col pt-6 pb-6 shadow-xl shrink-0 z-20">
      <div className="px-6 mb-8 flex items-center gap-2 cursor-pointer" onClick={() => navigate('/chat')}>
        <span className="text-brand-accent text-xl">▶</span>
        <h2 className="text-xl font-bold text-white tracking-tight">CineGuide AI</h2>
      </div>

      <div className="px-6 mb-8">
        <div className="flex items-center gap-3">
          <img src={avatarUrl} alt="Avatar" className="w-10 h-10 rounded-full bg-brand-card border border-brand-border" />
          <div className="overflow-hidden">
            <h3 className="text-white font-medium text-sm truncate">{user?.name || 'User'}</h3>
            <p className="text-brand-muted text-[11px] truncate">{user?.email || ''}</p>
          </div>
        </div>
      </div>

      <div className="px-6 mb-4">
        <div className="w-full h-[1px] bg-brand-border"></div>
      </div>

      <div className="flex-1 px-4 space-y-1 overflow-y-auto">
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-white/5 text-white font-medium text-sm border-l-2 border-brand-accent">
          <MessageSquare size={18} className="text-brand-accent" />
          New Chat
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-brand-muted hover:text-white hover:bg-white/5 transition-colors font-medium text-sm" onClick={() => alert('History feature coming soon')}>
          <Clock size={18} />
          History
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-brand-muted hover:text-white hover:bg-white/5 transition-colors font-medium text-sm" onClick={() => alert('Settings feature coming soon')}>
          <Settings size={18} />
          Settings
        </button>
      </div>

      <div className="px-6 mt-auto flex flex-col gap-4">
        <div className="pt-4 border-t border-brand-border">
          <p className="text-xs text-brand-placeholder text-center mb-4">
            Recommending movies nightly
          </p>
          <button 
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-brand-muted hover:text-white hover:bg-brand-accent/10 hover:border-brand-accent/20 border border-transparent transition-all text-sm font-medium"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
