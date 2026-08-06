import { useState } from 'react'

const API_BASE = 'http://127.0.0.1:8000/api'

function SendMoneyModal({ auth, onClose, onSuccess }) {
  const [recipientUsername, setRecipientUsername] = useState('')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (recipientUsername.trim().toLowerCase() === auth.user.username.toLowerCase()) {
      setError("You can't send money to yourself.")
      return
    }

    setLoading(true)
    try {
      const recipientRes = await fetch(`${API_BASE}/users/${encodeURIComponent(recipientUsername)}/recipient`)
      const recipientData = await recipientRes.json().catch(() => null)
      if (!recipientRes.ok) {
        throw new Error(recipientData?.detail || `Couldn't find user "${recipientUsername}"`)
      }

      const transferRes = await fetch(`${API_BASE}/transfers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${auth.access_token}`,
        },
        body: JSON.stringify({
          sender_account_id: auth.account.id,
          receiver_account_id: recipientData.account_id,
          amount: Number(amount),
          idempotency_key: crypto.randomUUID(),
        }),
      })
      const transferData = await transferRes.json().catch(() => null)
      if (!transferRes.ok) {
        throw new Error(transferData?.detail || `Transfer failed (status ${transferRes.status})`)
      }

      onSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(event) => event.stopPropagation()}>
        <form className="signup-form" onSubmit={handleSubmit}>
          <h2>Send money</h2>
          <p className="form-subtitle">Instantly transfer funds to another Payment Project user.</p>

          <label>
            Recipient username
            <input
              type="text"
              value={recipientUsername}
              onChange={(e) => setRecipientUsername(e.target.value)}
              placeholder="e.g. alice"
              required
            />
          </label>

          <label>
            Amount
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="0.00"
              required
            />
          </label>

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" disabled={loading}>
              {loading ? 'Sending…' : 'Send'}
            </button>
          </div>

          {error && <p className="error">{error}</p>}
        </form>
      </div>
    </div>
  )
}

export default SendMoneyModal
