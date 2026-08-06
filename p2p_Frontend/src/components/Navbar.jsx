import { Link } from 'react-router-dom'

function Navbar({ auth, onLogout }) {
  return (
    <nav className="navbar">
      <Link to="/" className="brand-badge">
        Payment Project
      </Link>
      <div className="navbar-actions">
        {auth ? (
          <button type="button" className="nav-link" onClick={onLogout}>
            Log Out
          </button>
        ) : (
          <>
            <Link to="/login" className="nav-link">
              Log In
            </Link>
            <Link to="/signup" className="nav-cta">
              Sign Up
            </Link>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar
