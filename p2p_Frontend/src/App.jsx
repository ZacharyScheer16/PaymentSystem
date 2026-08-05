import { useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000/api'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })

      if (!response.ok) {
        const body = await response.json().catch(() => null)
        throw new Error(
          body?.detail ? JSON.stringify(body.detail) : `Signup failed (status ${response.status})`
        )
      }

      const data = await response.json()
      setResult(data)
      setUsername('')
      setPassword('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div id="center">
      <h1>Payment Project</h1>

      <form className="signup-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>

        <label>
          Username
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            minLength={3}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? 'Creating account…' : 'Sign Up'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <h2>Welcome, {result.user.username}!</h2>
          <p>
            User ID: <code>{result.user.id}</code>
          </p>
          <p>
            Account ID: <code>{result.account.id}</code>
          </p>
          <p>
            Balance: {result.account.balance} {result.account.currency}
          </p>
        </div>
      )}
    </div>
  )
}

export default App
