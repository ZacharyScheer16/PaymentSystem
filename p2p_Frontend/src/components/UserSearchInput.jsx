import { useEffect, useRef, useState } from 'react'
import { API_BASE } from '../api'
import { initials } from '../format'

const DEBOUNCE_MS = 250

/**
 * Typeahead over the user directory — the shared input behind both "Add friend"
 * and the Send Money recipient field.
 *
 * `defaultOptions` are the rows shown while the box is still empty (Send Money
 * passes your friends there, so you can pick someone without typing at all).
 * `renderMeta` draws the right-hand side of a row — a badge, a button label —
 * and `clearOnSelect` decides whether picking someone empties the box (Add
 * friend) or leaves their name in it (Send Money).
 */
function UserSearchInput({
  auth,
  onSelect,
  onQueryChange,
  placeholder = 'Search by username…',
  defaultOptions = [],
  defaultLabel = '',
  renderMeta,
  clearOnSelect = false,
  initialQuery = '',
}) {
  const [query, setQuery] = useState(initialQuery)
  // `resultsFor` records which query `results` belong to. Comparing it against
  // what's currently typed derives "still loading" for free, and means a
  // response can never be mistaken for an answer to a different query.
  const [{ results, resultsFor, error }, setSearch] = useState({
    results: [],
    resultsFor: '',
    error: '',
  })
  const [open, setOpen] = useState(false)
  const [highlighted, setHighlighted] = useState(0)

  const containerRef = useRef(null)
  const listRef = useRef(null)

  const trimmed = query.trim()
  const loading = Boolean(trimmed) && resultsFor !== trimmed
  const options = trimmed ? (loading ? [] : results) : defaultOptions

  // Hovering row 3 and then having the list shrink under you would otherwise
  // leave `highlighted` pointing past the end.
  const activeIndex = Math.min(highlighted, Math.max(options.length - 1, 0))

  useEffect(() => {
    if (!trimmed) return undefined

    // One controller per keystroke. Aborting on cleanup stops a slow response
    // for "al" from landing after the quick one for "alice".
    const controller = new AbortController()

    const timer = setTimeout(async () => {
      try {
        const response = await fetch(
          `${API_BASE}/users/search?q=${encodeURIComponent(trimmed)}`,
          {
            headers: { Authorization: `Bearer ${auth.access_token}` },
            signal: controller.signal,
          },
        )
        if (!response.ok) {
          throw new Error(`Search failed (status ${response.status})`)
        }
        setSearch({ results: await response.json(), resultsFor: trimmed, error: '' })
      } catch (err) {
        if (err.name === 'AbortError') return
        setSearch({ results: [], resultsFor: trimmed, error: err.message })
      }
    }, DEBOUNCE_MS)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [trimmed, auth.access_token])

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Keep the highlighted row in view when arrowing past the visible window.
  useEffect(() => {
    const row = listRef.current?.children[activeIndex]
    row?.scrollIntoView({ block: 'nearest' })
  }, [activeIndex])

  function updateQuery(next) {
    setQuery(next)
    onQueryChange?.(next)
  }

  function choose(user) {
    updateQuery(clearOnSelect ? '' : user.username)
    setOpen(false)
    setHighlighted(0)
    onSelect(user)
  }

  function handleKeyDown(event) {
    if (event.key === 'Escape') {
      setOpen(false)
      return
    }
    if (!open || options.length === 0) {
      // ArrowDown on a closed box reopens it rather than doing nothing.
      if (event.key === 'ArrowDown') setOpen(true)
      return
    }
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setHighlighted((prev) => (prev + 1) % options.length)
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setHighlighted((prev) => (prev - 1 + options.length) % options.length)
    } else if (event.key === 'Enter') {
      // Stop the form from submitting — Enter here means "pick this person".
      event.preventDefault()
      choose(options[activeIndex])
    }
  }

  const showDropdown = open && Boolean(loading || error || options.length > 0 || trimmed)

  return (
    <div className="typeahead" ref={containerRef}>
      <input
        type="text"
        className="typeahead-input"
        role="combobox"
        aria-expanded={showDropdown}
        aria-autocomplete="list"
        aria-controls="typeahead-listbox"
        autoComplete="off"
        placeholder={placeholder}
        value={query}
        onChange={(event) => {
          updateQuery(event.target.value)
          setHighlighted(0)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={handleKeyDown}
      />

      {showDropdown && (
        <div className="typeahead-dropdown">
          {!trimmed && defaultLabel && options.length > 0 && (
            <p className="typeahead-section-label">{defaultLabel}</p>
          )}

          {loading && <p className="typeahead-status">Searching…</p>}
          {!loading && error && <p className="typeahead-status typeahead-error">{error}</p>}
          {!loading && !error && trimmed && options.length === 0 && (
            <p className="typeahead-status">No users matching “{trimmed}”</p>
          )}

          {options.length > 0 && (
            <ul className="typeahead-list" id="typeahead-listbox" role="listbox" ref={listRef}>
              {options.map((user, index) => (
                <li
                  key={user.id}
                  role="option"
                  aria-selected={index === activeIndex}
                  className={`typeahead-option${index === activeIndex ? ' is-highlighted' : ''}`}
                  onMouseEnter={() => setHighlighted(index)}
                  // mousedown, not click: the input's blur would otherwise close
                  // the dropdown out from under the pointer first.
                  onMouseDown={(event) => {
                    event.preventDefault()
                    choose(user)
                  }}
                >
                  <span className="typeahead-avatar" aria-hidden="true">
                    {initials(user.username)}
                  </span>
                  <span className="typeahead-username">{user.username}</span>
                  {renderMeta && <span className="typeahead-meta">{renderMeta(user)}</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

export default UserSearchInput
