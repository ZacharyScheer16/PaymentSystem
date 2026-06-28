import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [message, setMessage] = useState("Loading...")

  // THIS IS THE BRIDGE
  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(err => setMessage("Error connecting to backend"))
  }, [])

  return (
    <div>
      <h1>Payment Project</h1>
      <p>Backend says: <strong>{message}</strong></p>
    </div>
  )
}

export default App