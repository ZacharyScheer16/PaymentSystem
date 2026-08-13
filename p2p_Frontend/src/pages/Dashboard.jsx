import { useCallback, useEffect, useState } from 'react'
import SendMoneyModal from '../components/SendMoneyModal'
import DepositModal from '../components/DepositModal'
import { API_BASE } from '../api'
import { formatDate, initials } from '../format'

function Dashboard({ auth, onBalanceChange }) {
  const { user, account } = auth
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showSendModal, setShowSendModal] = useState(false)
  const [showDepositModal, setShowDepositModal] = useState(false)

  const loadTransactions = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_BASE}/accounts/${account.id}/transfers`)
      if (!response.ok) {
        throw new Error(`Failed to load transactions (status ${response.status})`)
      }
      const data = await response.json()
      setTransactions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [account.id])

  useEffect(() => {
    let cancelled = false
    async function run() {
      await loadTransactions()
      if (cancelled) return
    }
    run()
    return () => {
      cancelled = true
    }
  }, [loadTransactions])

  async function refreshAccount() {
    const response = await fetch(`${API_BASE}/accounts/${account.id}`)
    if (response.ok) {
      const data = await response.json()
      onBalanceChange(data)
    }
  }

  async function handleSendSuccess() {
    setShowSendModal(false)
    await Promise.all([loadTransactions(), refreshAccount()])
  }

  async function handleDepositSuccess(updatedAccount) {
    setShowDepositModal(false)
    // The deposit endpoint returns the updated account, so the balance comes
    // straight from the response — no extra refreshAccount() round trip. The
    // deposit does write a CREDIT ledger entry though, so reload the activity.
    onBalanceChange(updatedAccount)
    await loadTransactions()
  }

  return (
    <div className="dashboard">
      <div className="dashboard-inner">
        <header className="dashboard-header">
          <div className="dashboard-avatar" aria-hidden="true">
            {initials(user.username)}
          </div>
          <div>
            <p className="dashboard-greeting">Welcome back</p>
            <h1 className="dashboard-username">{user.username}</h1>
          </div>
        </header>

        <section className="balance-card">
          <span className="balance-label">Available balance</span>
          <span className="balance-amount">
            {Number(account.balance).toFixed(2)} <span className="balance-currency">{account.currency}</span>
          </span>
          <div className="balance-actions">
            <button type="button" className="send-money-btn" onClick={() => setShowSendModal(true)}>
              Send Money
            </button>
            <button type="button" className="add-money-btn" onClick={() => setShowDepositModal(true)}>
              Add Money
            </button>
          </div>
        </section>

        <section className="activity-card">
          <h2 className="activity-heading">Recent activity</h2>

          {loading && <p className="form-subtitle">Loading…</p>}
          {error && <p className="error">{error}</p>}

          {!loading && !error && transactions.length === 0 && (
            <p className="empty-state">No transactions yet — send or receive money to see activity here.</p>
          )}

          {!loading && !error && transactions.length > 0 && (
            <ul className="transaction-list">
              {transactions.slice(0, 10).map((entry) => (
                <li key={entry.id} className="transaction-item">
                  <div className="transaction-icon" data-type={entry.entry_type}>
                    {entry.entry_type === 'DEBIT' ? '↑' : '↓'}
                  </div>
                  <div className="transaction-details">
                    <span className="transaction-type">{entry.entry_type === 'DEBIT' ? 'Sent' : 'Received'}</span>
                    <span className="transaction-date">{formatDate(entry.created_at)}</span>
                  </div>
                  <span className={`transaction-amount ${entry.entry_type === 'DEBIT' ? 'negative' : 'positive'}`}>
                    {entry.entry_type === 'DEBIT' ? '-' : '+'}
                    {Number(entry.amount).toFixed(2)} {account.currency}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {showSendModal && (
        <SendMoneyModal auth={auth} onClose={() => setShowSendModal(false)} onSuccess={handleSendSuccess} />
      )}

      {showDepositModal && (
        <DepositModal auth={auth} onClose={() => setShowDepositModal(false)} onSuccess={handleDepositSuccess} />
      )}
    </div>
  )
}

export default Dashboard
