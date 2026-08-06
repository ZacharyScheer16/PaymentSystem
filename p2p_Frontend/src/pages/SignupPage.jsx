import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

const API_BASE = 'http://127.0.0.1:8000/api'

function SignupPage({ auth, onAuthSuccess }) {
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
      const response = await fetch(`${API_BASE}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        throw new Error(data?.detail || `Signup failed (status ${response.status})`)
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
          <h2>Create an account</h2>
          <p className="form-subtitle">Get a free account with instant transfers.</p>

          <label>
            Username
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>

          <label>
            Password
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Please wait…' : 'Sign Up'}
          </button>
        </form>

        <p className="form-switch">
          Already have an account?{' '}
          <Link to="/login" className="text-link">
            Log in
          </Link>
        </p>

        {error && <p className="error">{error}</p>}
      </div>
    </div>
  )
}

export default SignupPage
