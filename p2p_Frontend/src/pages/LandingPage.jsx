import { Link } from 'react-router-dom'

const FEATURES = [
  {
    title: 'Instant transfers',
    text: 'Send money to any account in real time, backed by an atomic ledger.',
  },
  {
    title: 'Secure by design',
    text: 'Passwords are hashed with bcrypt; every request is verified with a signed token.',
  },
  {
    title: 'Full audit trail',
    text: 'Every transfer records a matching debit and credit — nothing is ever lost.',
  },
]

function LandingPage() {
  return (
    <div className="landing">
      <div className="landing-brand">
        <h1>Send money the moment it matters.</h1>
        <p className="landing-subtitle">
          A peer-to-peer payments platform built on a double-entry ledger — every transfer is
          atomic, auditable, and instant.
        </p>

        <ul className="feature-list">
          {FEATURES.map((feature) => (
            <li key={feature.title}>
              <span className="feature-mark">&#10003;</span>
              <div>
                <strong>{feature.title}</strong>
                <p>{feature.text}</p>
              </div>
            </li>
          ))}
        </ul>

        <div className="landing-cta">
          <Link to="/signup" className="nav-cta">
            Get Started
          </Link>
          <Link to="/login" className="nav-link">
            Log In
          </Link>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
