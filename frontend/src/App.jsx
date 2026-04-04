import { useState, useEffect } from 'react'
import { useAuth } from './context/AuthContext'
import Landing from './components/Landing'
import Auth from './components/Auth'
import Chat from './components/Chat'

function App() {
  const { isAuthenticated } = useAuth();
  const [currentRoute, setCurrentRoute] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => {
      setCurrentRoute(window.location.pathname);
    };
    window.addEventListener('popstate', handleLocationChange);
    return () => window.removeEventListener('popstate', handleLocationChange);
  }, []);

  const navigate = (path) => {
    window.history.pushState({}, '', path);
    setCurrentRoute(path);
  };

  // Auth protection logic
  if (isAuthenticated && (currentRoute === '/' || currentRoute === '/login' || currentRoute === '/register')) {
    navigate('/chat');
    return null;
  }

  if (!isAuthenticated && currentRoute === '/chat') {
    navigate('/');
    return null;
  }

  // Router switch
  if (currentRoute === '/') {
    return <Landing navigate={navigate} />;
  } else if (currentRoute === '/login') {
    return <Auth navigate={navigate} view="login" />;
  } else if (currentRoute === '/register') {
    return <Auth navigate={navigate} view="register" />;
  } else if (currentRoute === '/chat') {
    return <Chat navigate={navigate} />;
  }

  return <Landing navigate={navigate} />;
}

export default App;
