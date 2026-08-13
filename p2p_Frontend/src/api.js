// Single source of truth for the API base URL, plus the small request helpers
// shared by more than one component.
//
// API_BASE defaults to the relative "/api" — in both `npm run dev` (Vite proxy)
// and the Docker image (nginx proxy), requests go to the same origin serving the
// page, so nothing host-specific is baked into the bundle at build time.
//
// VITE_API_BASE overrides it for the case where the API lives on a different
// origin (e.g. a separately deployed backend). Note it is read at BUILD time,
// not runtime — changing it requires rebuilding the frontend.
export const API_BASE = import.meta.env.VITE_API_BASE || '/api'

function authHeaders(auth) {
  return { Authorization: `Bearer ${auth.access_token}` }
}

/** Read the error the backend actually sent, falling back to the status code. */
async function errorFrom(response, fallback) {
  const body = await response.json().catch(() => null)
  return new Error(body?.detail || `${fallback} (status ${response.status})`)
}

// The friends list is loaded by both FriendsPage and SendMoneyModal, so these
// live here rather than being written twice.

export async function fetchFriends(auth, signal) {
  const response = await fetch(`${API_BASE}/friends/`, { headers: authHeaders(auth), signal })
  if (!response.ok) throw await errorFrom(response, "Couldn't load friends")
  return response.json()
}

export async function addFriend(auth, username) {
  const response = await fetch(`${API_BASE}/friends/`, {
    method: 'POST',
    headers: { ...authHeaders(auth), 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  })
  if (!response.ok) throw await errorFrom(response, `Couldn't add ${username}`)
  return response.json()
}

export async function removeFriend(auth, friendId) {
  const response = await fetch(`${API_BASE}/friends/${friendId}`, {
    method: 'DELETE',
    headers: authHeaders(auth),
  })
  if (!response.ok) throw await errorFrom(response, "Couldn't remove friend")
}
