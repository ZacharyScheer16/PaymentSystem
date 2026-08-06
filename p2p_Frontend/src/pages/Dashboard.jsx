function Dashboard({ auth }) {
  const { user, account } = auth

  return (
    <div className="page-content">
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
      </div>
    </div>
  )
}

export default Dashboard
