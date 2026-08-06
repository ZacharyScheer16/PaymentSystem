import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import './App.css'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'

function App() {
  const [auth, setAuth] = useState(null)

  return (
    <div className="page">
      <Navbar auth={auth} onLogout={() => setAuth(null)} />
      <Routes>
        <Route
          path="/"
          element={
            auth ? (
              <Dashboard
                auth={auth}
                onBalanceChange={(account) => setAuth((prev) => ({ ...prev, account }))}
              />
            ) : (
              <LandingPage />
            )
          }
        />
        <Route path="/login" element={<LoginPage auth={auth} onAuthSuccess={setAuth} />} />
        <Route path="/signup" element={<SignupPage auth={auth} onAuthSuccess={setAuth} />} />
      </Routes>
    </div>
  )
}

export default App
