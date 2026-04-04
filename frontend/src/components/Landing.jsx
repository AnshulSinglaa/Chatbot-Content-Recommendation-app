import React from 'react';
import { motion } from 'framer-motion';
import { Search, Brain, Zap, Heart } from 'lucide-react';

const Landing = ({ navigate }) => {
  return (
    <div className="min-h-screen bg-brand-primary overflow-hidden relative font-sans flex flex-col">
      {/* Animated blobs using tailwind custom rules implicitly, or pure inline css for now */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-brand-accent/20 rounded-full blur-[120px] mix-blend-screen"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-purple-900/20 rounded-full blur-[150px] mix-blend-screen"></div>

      <main className="flex-grow max-w-[1200px] mx-auto px-6 pt-24 pb-16 relative z-10 w-full flex flex-col items-center">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-3xl"
        >
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-white mb-6">
            Find Your Perfect Movie Tonight
          </h1>
          <p className="text-xl text-brand-muted mb-10 leading-relaxed">
            AI-powered recommendations that understand your mood, not just your genre.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/register')}
              className="px-8 py-4 bg-brand-accent hover:bg-brand-accent-hover transition-colors text-white font-medium rounded-full text-lg shadow-lg outline-none border-none w-full sm:w-auto"
            >
              Get Started Free
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => navigate('/login')}
              className="px-8 py-4 bg-transparent border border-brand-border text-white hover:bg-white/5 transition-colors font-medium rounded-full text-lg w-full sm:w-auto"
            >
              Sign In
            </motion.button>
          </div>
          
          <p className="text-sm text-brand-placeholder flex items-center justify-center gap-2">
            9,800+ movies <span className="w-1 h-1 rounded-full bg-brand-placeholder"></span> Mood-aware AI <span className="w-1 h-1 rounded-full bg-brand-placeholder"></span> Instant recommendations
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6 w-full mt-32">
          {features.map((f, i) => (
            <motion.div
               key={i}
               initial={{ opacity: 0, y: 20 }}
               whileInView={{ opacity: 1, y: 0 }}
               viewport={{ once: true }}
               transition={{ delay: i * 0.1 }}
               className="glass-panel p-8 rounded-2xl flex flex-col items-start"
            >
              <div className="p-3 bg-white/5 border border-brand-border/50 rounded-xl mb-6 text-brand-accent">
                {f.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
              <p className="text-brand-muted leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>

        <div className="w-full mt-32 mb-16">
          <h2 className="text-3xl font-bold text-center text-white mb-16">How it works</h2>
          <div className="flex flex-col md:flex-row items-center justify-between relative gap-10">
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-[1px] bg-brand-border -z-10 translate-y-[20px]"></div>
            {steps.map((s, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex flex-col items-center relative bg-brand-primary px-8"
              >
                <div className="absolute -top-6 -z-10 text-[100px] font-bold text-brand-card leading-none select-none">
                  {i + 1}
                </div>
                <h4 className="text-lg font-medium text-white mt-12">{s}</h4>
              </motion.div>
            ))}
          </div>
        </div>
      </main>

      <footer className="py-8 border-t border-brand-border mt-auto">
        <p className="text-brand-placeholder flex items-center justify-center gap-2">
          CineGuide AI <span className="text-xs">&bull;</span> Built with <Heart size={14} className="text-brand-accent" fill="currentColor" /> for movie lovers
        </p>
      </footer>
    </div>
  );
};

const features = [
  { icon: <Search size={24} />, title: "Understands What You Mean", desc: "No more scrolling through endless genre lists. Just type exactly what you're craving naturally." },
  { icon: <Brain size={24} />, title: "Mood Detection", desc: "Our AI analyzes the subtle nuances of your request to match your exact vibe and context." },
  { icon: <Zap size={24} />, title: "Instant Results", desc: "Powered by vector-search to bring you perfect cinematic choices in mere milliseconds." }
];

const steps = ["Describe your mood", "AI finds matches", "Get recommendations"];

export default Landing;
