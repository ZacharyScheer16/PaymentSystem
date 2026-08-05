import { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000/api'

function AuthPage({ onAuthSuccess }) {
  const [mode, setMode] = useState('signup') // 'signup' | 'login'
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const isSignup = mode === 'signup'

  function switchMode(nextMode) {
    setMode(nextMode)
    setError('')
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    const endpoint = isSignup ? '/users/' : '/users/login'

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(data?.detail || `${isSignup ? 'Signup' : 'Login'} failed (status ${response.status})`)
      }

      onAuthSuccess(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div id="center">
      <h1>Payment Project</h1>

      <div className="auth-toggle">
        <button type="button" className={isSignup ? 'active' : ''} onClick={() => switchMode('signup')}>
          Sign Up
        </button>
        <button type="button" className={!isSignup ? 'active' : ''} onClick={() => switchMode('login')}>
          Log In
        </button>
      </div>

      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>{isSignup ? 'Create an account' : 'Welcome back'}</h2>

        <label>
          Username
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>

        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Please wait…' : isSignup ? 'Sign Up' : 'Log In'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </div>
  )
}

export default AuthPage
