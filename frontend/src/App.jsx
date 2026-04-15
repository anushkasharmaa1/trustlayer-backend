import { useMemo, useState } from 'react';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';

function App() {
  const [view, setView] = useState('landing');

  const page = useMemo(() => {
    if (view === 'dashboard') {
      return <Dashboard onBack={() => setView('landing')} />;
    }
    return <LandingPage onStart={() => setView('dashboard')} />;
  }, [view]);

  return <div className="app-shell">{page}</div>;
}

export default App;
