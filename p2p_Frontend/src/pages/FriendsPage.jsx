import { useEffect, useState } from 'react'
import UserSearchInput from '../components/UserSearchInput'
import SendMoneyModal from '../components/SendMoneyModal'
import { API_BASE, addFriend, fetchFriends, removeFriend } from '../api'
import { initials } from '../format'

function FriendsPage({ auth, onBalanceChange }) {
  const [friends, setFriends] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [sendTo, setSendTo] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    fetchFriends(auth, controller.signal)
      .then((data) => {
        setFriends(data)
        setLoading(false)
      })
      .catch((err) => {
        if (err.name === 'AbortError') return
        setError(err.message)
        setLoading(false)
      })

    return () => controller.abort()
  }, [auth])

  // The search dropdown flags who's already saved, so re-running the search
  // after an add isn't needed — but the list below does have to refresh.
  const friendIds = new Set(friends.map((friend) => friend.id))

  async function handleAdd(user) {
    if (friendIds.has(user.id)) return
    setError('')
    try {
      const friend = await addFriend(auth, user.username)
      setFriends((prev) => [...prev, friend].sort((a, b) => a.username.localeCompare(b.username)))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleRemove(friend) {
    setError('')
    try {
      await removeFriend(auth, friend.id)
      setFriends((prev) => prev.filter((entry) => entry.id !== friend.id))
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleSendSuccess() {
    setSendTo(null)
    // The balance in the navbar/dashboard is stale after a send, so re-read it.
    const response = await fetch(`${API_BASE}/accounts/${auth.account.id}`)
    if (response.ok) onBalanceChange(await response.json())
  }

  return (
    <div className="dashboard">
      <div className="dashboard-inner">
        <header className="dashboard-header">
          <div>
            <p className="dashboard-greeting">Your people</p>
            <h1 className="dashboard-username">Friends</h1>
          </div>
        </header>

        <section className="activity-card">
          <h2 className="activity-heading">Add a friend</h2>
          <p className="form-subtitle">
            Start typing a username — matching people appear as you type.
          </p>

          <div className="friend-search-wrap">
            <UserSearchInput
              auth={auth}
              onSelect={handleAdd}
              clearOnSelect
              placeholder="Search users…"
              renderMeta={(user) =>
                user.is_friend || friendIds.has(user.id) ? (
                  <span className="typeahead-badge is-muted">Added</span>
                ) : (
                  <span className="typeahead-badge">Add</span>
                )
              }
            />
          </div>

          {error && <p className="error">{error}</p>}
        </section>

        <section className="activity-card">
          <h2 className="activity-heading">Your friends</h2>

          {loading && <p className="form-subtitle">Loading…</p>}

          {!loading && friends.length === 0 && (
            <p className="empty-state">
              No friends yet — search above to save someone you pay often.
            </p>
          )}

          {!loading && friends.length > 0 && (
            <ul className="friend-list">
              {friends.map((friend) => (
                <li key={friend.id} className="friend-item">
                  <div className="friend-avatar" aria-hidden="true">
                    {initials(friend.username)}
                  </div>
                  <span className="friend-username">{friend.username}</span>
                  <div className="friend-actions">
                    <button type="button" className="btn-small" onClick={() => setSendTo(friend)}>
                      Send
                    </button>
                    <button
                      type="button"
                      className="btn-small btn-danger"
                      onClick={() => handleRemove(friend)}
                      aria-label={`Remove ${friend.username}`}
                    >
                      Remove
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {sendTo && (
        <SendMoneyModal
          // Keyed so switching recipients remounts rather than keeping the
          // previous person's name in the (uncontrolled) search box.
          key={sendTo.id}
          auth={auth}
          initialRecipient={sendTo.username}
          onClose={() => setSendTo(null)}
          onSuccess={handleSendSuccess}
        />
      )}
    </div>
  )
}

export default FriendsPage
