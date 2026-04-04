import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Eye, EyeOff, CheckCircle2, XCircle } from 'lucide-react';
import { fetchApi } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const Auth = ({ navigate, view = 'login' }) => {
  const isLogin = view === 'login';
  const { login } = useAuth();
  
  const [formData, setFormData] = useState({ name: '', email: '', password: '', confirmPassword: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Password strength logic (simple)
  const getPasswordStrength = () => {
    const pw = formData.password;
    if (!pw) return 0;
    let strength = 0;
    if (pw.length > 5) strength += 33;
    if (pw.length > 8) strength += 33;
    if (/[A-Z]/.test(pw) && /[0-9]/.test(pw)) strength += 34;
    return strength;
  };
  
  const strength = getPasswordStrength();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!isLogin && formData.password !== formData.confirmPassword) {
      return setError("Passwords do not match");
    }
    
    setLoading(true);
    try {
      if (isLogin) {
        const data = await fetchApi('/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email: formData.email, password: formData.password })
        });
        const currentUser = await fetchApi('/auth/me', { headers: { 'Authorization': `Bearer ${data.access_token}`}});
        login(data.access_token, currentUser);
        navigate('/chat');
      } else {
        const data = await fetchApi('/auth/signup', {
          method: 'POST',
          body: JSON.stringify({ name: formData.name, email: formData.email, password: formData.password })
        });
        const currentUser = await fetchApi('/auth/me', { headers: { 'Authorization': `Bearer ${data.access_token}`}});
        login(data.access_token, currentUser);
        navigate('/chat');
      }
    } catch (err) {
      setError(err.message || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-brand-primary text-brand-text font-sans selection:bg-brand-accent/30">
      
      {/* Left Abstract Side */}
      <div className="hidden lg:flex w-1/2 bg-brand-secondary relative overflow-hidden flex-col justify-center p-20">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-brand-accent/10 rounded-full blur-[100px] mix-blend-screen"></div>
        <div className="absolute bottom-[10%] right-[-10%] w-[40%] h-[40%] bg-blue-900/10 rounded-full blur-[100px] mix-blend-screen"></div>
        
        <div className="relative z-10 max-w-lg">
          <h1 className="text-4xl font-bold mb-6 text-white leading-tight">
            Discover movies that match your exact vibe.
          </h1>
          <p className="text-xl text-brand-muted">
            CineGuide AI understands your mood and context to offer the perfect cinematic recommendations.
          </p>
        </div>

        {/* Abstract Geometric Shapes */}
        <div className="absolute inset-0 z-0 opacity-20 pointer-events-none">
           <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.2)" strokeWidth="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
           </svg>
        </div>
      </div>

      {/* Right Form Side */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-brand-primary relative">
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-full max-w-md bg-brand-card p-10 rounded-2xl border border-brand-border shadow-2xl relative"
        >
          <div className="mb-10 cursor-pointer w-max" onClick={() => navigate('/')}>
             <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
               <span className="text-brand-accent">▶</span> CineGuide
             </h2>
          </div>

          <h3 className="text-3xl font-bold text-white mb-2">
            {isLogin ? 'Welcome back' : 'Create an account'}
          </h3>
          <p className="text-brand-muted mb-8 leading-relaxed">
            {isLogin ? 'Sign in to access your AI movie assistant.' : 'Join the new era of film discovery.'}
          </p>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-brand-accent/10 border border-brand-accent/20 text-brand-accent flex items-start gap-3 text-sm">
              <XCircle size={18} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {!isLogin && (
               <div>
                  <label className="block text-sm font-medium text-brand-muted mb-2">Full Name</label>
                  <input 
                    type="text" 
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full bg-brand-primary border border-brand-border rounded-xl px-4 py-3 text-white placeholder-brand-placeholder focus:outline-none focus:border-brand-accent transition-colors"
                  />
               </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-brand-muted mb-2">Email Address</label>
              <input 
                type="email" 
                required
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full bg-brand-primary border border-brand-border rounded-xl px-4 py-3 text-white placeholder-brand-placeholder focus:outline-none focus:border-brand-accent transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-brand-muted mb-2">Password</label>
              <div className="relative">
                <input 
                  type={showPassword ? "text" : "password"} 
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-brand-primary border border-brand-border rounded-xl px-4 py-3 text-white placeholder-brand-placeholder focus:outline-none focus:border-brand-accent transition-colors pr-12"
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-brand-placeholder hover:text-brand-muted transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>

              {/* Strength Indicator */}
              {!isLogin && formData.password && (
                <div className="mt-3">
                  <div className="h-1.5 w-full bg-brand-primary rounded-full overflow-hidden flex gap-1">
                    <div className={`h-full flex-1 rounded-full transition-all duration-300 ${strength > 0 ? (strength > 33 ? (strength > 66 ? 'bg-brand-success' : 'bg-yellow-500') : 'bg-brand-accent') : 'bg-transparent'}`}></div>
                    <div className={`h-full flex-1 rounded-full transition-all duration-300 ${strength > 33 ? (strength > 66 ? 'bg-brand-success' : 'bg-yellow-500') : 'bg-transparent'}`}></div>
                    <div className={`h-full flex-1 rounded-full transition-all duration-300 ${strength > 66 ? 'bg-brand-success' : 'bg-transparent'}`}></div>
                  </div>
                  <p className="text-xs text-brand-muted mt-2 text-right">
                    {strength <= 33 ? 'Weak' : strength <= 66 ? 'Medium' : 'Strong'}
                  </p>
                </div>
              )}
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-brand-muted mb-2">Confirm Password</label>
                <div className="relative">
                  <input 
                    type={showPassword ? "text" : "password"} 
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                    className="w-full bg-brand-primary border border-brand-border rounded-xl px-4 py-3 text-white placeholder-brand-placeholder focus:outline-none focus:border-brand-accent transition-colors pr-12"
                  />
                  {formData.confirmPassword && formData.confirmPassword === formData.password && (
                    <div className="absolute right-4 top-1/2 -translate-y-1/2 text-brand-success">
                      <CheckCircle2 size={18} />
                    </div>
                  )}
                </div>
              </div>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              disabled={loading}
              type="submit"
              className="w-full bg-brand-accent hover:bg-brand-accent-hover text-white font-medium py-3.5 rounded-xl transition-colors mt-4 shadow-lg shadow-brand-accent/20 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
            </motion.button>
          </form>

          <div className="mt-8 text-center text-sm text-brand-muted">
            {isLogin ? (
               <p>
                 Don't have an account?{' '}
                 <button onClick={() => navigate('/register')} className="text-white hover:text-brand-accent transition-colors underline underline-offset-4 font-medium">Create one</button>
               </p>
            ) : (
               <p>
                 Already have an account?{' '}
                 <button onClick={() => navigate('/login')} className="text-white hover:text-brand-accent transition-colors underline underline-offset-4 font-medium">Sign In</button>
               </p>
            )}
          </div>
          
          {isLogin && (
             <div className="mt-4 text-center">
                 <button 
                   onClick={() => alert("Feature coming soon!")} 
                   className="text-xs text-brand-placeholder hover:text-brand-muted transition-colors"
                 >
                   Forgot password?
                 </button>
             </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Auth;
