// Small presentation helpers shared across pages. Kept out of component files
// so importing them doesn't break React Fast Refresh.

/** Two-letter avatar initials for a username. */
export function initials(username) {
  return username.slice(0, 2).toUpperCase()
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
