function Dashboard({ auth, onLogout }) {
  const { user, account } = auth

  return (
    <div id="center">
      <h1>Payment Project</h1>
      <div className="result">
        <h2>Welcome, {user.username}!</h2>
        <p>
          User ID: <code>{user.id}</code>
        </p>
        <p>
          Account ID: <code>{account.id}</code>
        </p>
        <p>
          Balance: {account.balance} {account.currency}
        </p>
        <button onClick={onLogout}>Log Out</button>
      </div>
    </div>
  )
}

export default Dashboard
