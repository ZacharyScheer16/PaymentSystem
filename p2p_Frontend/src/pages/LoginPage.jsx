import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:8000/api'

function LoginPage({ auth, onAuthSuccess }) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (auth) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(data?.detail || `Login failed (status ${response.status})`)
      }

      onAuthSuccess(data)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-panel">
      <div className="auth-card">
        <form className="signup-form" onSubmit={handleSubmit}>
          <h2>Welcome back</h2>
          <p className="form-subtitle">Log in to view your balance and send money.</p>

          <label>
            Username
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Please wait…' : 'Log In'}
          </button>
        </form>

        <p className="form-switch">
          Don&apos;t have an account?{' '}
          <Link to="/signup" className="text-link">
            Sign up
          </Link>
        </p>

        {error && <p className="error">{error}</p>}
      </div>
    </div>
  )
}

export default LoginPage
