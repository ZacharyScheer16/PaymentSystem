import { useEffect, useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000/api'

function formatDate(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function Dashboard({ auth }) {
  const { user, account } = auth
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadTransactions() {
      setLoading(true)
      setError('')
      try {
        const response = await fetch(`${API_BASE}/accounts/${account.id}/transfers`)
        if (!response.ok) {
          throw new Error(`Failed to load transactions (status ${response.status})`)
        }
        const data = await response.json()
        if (!cancelled) {
          setTransactions(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadTransactions()
    return () => {
      cancelled = true
    }
  }, [account.id])

  return (
    <div className="page-content">
      <div className="result">
        <h2>Welcome, {user.username}!</h2>
        <p className="balance-display">
          {account.balance} {account.currency}
        </p>

        <h3 className="transactions-heading">Recent transactions</h3>

        {loading && <p className="form-subtitle">Loading…</p>}
        {error && <p className="error">{error}</p>}

        {!loading && !error && transactions.length === 0 && (
          <p className="form-subtitle">No transactions yet.</p>
        )}

        {!loading && !error && transactions.length > 0 && (
          <ul className="transaction-list">
            {transactions.slice(0, 10).map((entry) => (
              <li key={entry.id} className="transaction-item">
                <div>
                  <span className="transaction-type">{entry.entry_type === 'DEBIT' ? 'Sent' : 'Received'}</span>
                  <span className="transaction-date">{formatDate(entry.created_at)}</span>
                </div>
                <span className={`transaction-amount ${entry.entry_type === 'DEBIT' ? 'negative' : 'positive'}`}>
                  {entry.entry_type === 'DEBIT' ? '-' : '+'}
                  {entry.amount} {account.currency}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

export default Dashboard
