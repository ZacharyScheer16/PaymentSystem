import { useState } from 'react'
import './App.css'
import AuthPage from './components/AuthPage'
import Dashboard from './components/Dashboard'

function App() {
  const [auth, setAuth] = useState(null)

  if (!auth) {
    return <AuthPage onAuthSuccess={setAuth} />
  }

  return <Dashboard auth={auth} onLogout={() => setAuth(null)} />
}

export default App
