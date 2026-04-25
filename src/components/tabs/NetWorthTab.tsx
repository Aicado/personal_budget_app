import React, { useState, useEffect } from 'react'
import './Tabs.css'

interface Account {
  name: string
  balance: number
  type: string
  is_asset: boolean
}

interface CurrentBalances {
  accounts: Account[]
  total_assets: number
  total_debt: number
  net_worth: number
}

export const NetWorthTab: React.FC = () => {
  const [balanceData, setBalanceData] = useState<CurrentBalances | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCurrentBalances = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/net-worth/current-balances')
      if (!response.ok) {
        throw new Error('Failed to fetch current account balances')
      }
      const data = await response.json()
      const normalizedAccounts = (data.accounts || []).map((account: { name?: string; type?: string; is_asset?: boolean; net_value?: number; balance?: number }) => ({
        name: account.name || 'Unknown',
        type: account.type || 'Unknown',
        is_asset: account.is_asset ?? (account.type ? account.type.toLowerCase().indexOf('credit') === -1 && account.type.toLowerCase().indexOf('debt') === -1 : true),
        balance: typeof account.net_value === 'number' ? account.net_value : typeof account.balance === 'number' ? account.balance : 0,
      }))
      setBalanceData({
        accounts: normalizedAccounts,
        total_assets: data.total_assets || 0,
        total_debt: data.total_debt || 0,
        net_worth: data.net_worth || 0,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const timer = setTimeout(() => {
      void fetchCurrentBalances()
    }, 0)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="net-worth-tab">
      <div className="tab-header">
        <h2><span aria-hidden="true">📊</span> Net Worth Report</h2>
        <p>Current account balances and net worth</p>
        <button className="btn btn-primary" onClick={fetchCurrentBalances} disabled={loading}>
          {loading && <span className="spinner" aria-hidden="true"></span>}
          {loading ? 'Loading...' : 'Refresh Balances'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading current balances...</div>
      ) : balanceData ? (
        <>
          <div className="net-worth-summary">
            <div className="nw-card assets-card">
              <div className="nw-label">Total Assets</div>
              <div className="nw-value value-positive">
                ${balanceData.total_assets.toFixed(2)}
              </div>
            </div>
            <div className="nw-card debt-card">
              <div className="nw-label">Total Debt</div>
              <div className="nw-value value-negative">
                ${balanceData.total_debt.toFixed(2)}
              </div>
            </div>
            <div className="nw-card net-card">
              <div className="nw-label">Net Worth</div>
              <div className={`nw-value ${balanceData.net_worth >= 0 ? 'value-positive' : 'value-negative'}`}>
                ${balanceData.net_worth.toFixed(2)}
              </div>
            </div>
          </div>

          <div className="net-worth-table">
            <h3>Account Balances</h3>
            <table>
              <thead>
                <tr>
                  <th>Account Name</th>
                  <th>Type</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody>
                {balanceData.accounts.map((account, idx) => (
                  <tr key={idx}>
                    <td>{account.name}</td>
                    <td>{account.type}</td>
                    <td className={account.balance >= 0 ? 'value-positive' : 'value-negative'}>
                      ${account.balance.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="no-data">
          <p>No account balance data available. Please ensure current.csv exists in the data directory.</p>
        </div>
      )}
    </div>
  )
}
