import React, { useState, useEffect } from 'react'
import './Tabs.css'

interface AccountInfo {
  name: string
  transaction_count: number
  date_range: {
    start: string
    end: string
  }
  totals: {
    inflow: number
    outflow: number
    net: number
  }
}

export const AccountsTab: React.FC = () => {
  const [accounts, setAccounts] = useState<AccountInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/database/files')
      if (!response.ok) {
        throw new Error('Failed to fetch accounts data')
      }
      const data = await response.json()
      // Transform data for display
      setAccounts(data.files || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="accounts-tab">
      <div className="tab-header">
        <h2>💳 Accounts</h2>
        <p>View all accounts and their transaction summary</p>
        <button className="btn btn-primary" onClick={fetchAccounts} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh Accounts'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading accounts...</div>
      ) : (
        <div className="accounts-grid">
          {accounts.length === 0 ? (
            <div className="no-data">
              <p>No accounts found. Try uploading a CSV file first.</p>
            </div>
          ) : (
            accounts.map((account, idx) => (
              <div key={idx} className="account-card">
                <div className="account-header">
                  <h3>{account.name}</h3>
                </div>
                <div className="account-details">
                  <div className="detail-item">
                    <span className="label">Transactions:</span>
                    <span className="value">{account.transaction_count}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Date Range:</span>
                    <span className="value">{account.date_range?.start || 'N/A'} to {account.date_range?.end || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Total Inflow:</span>
                    <span className="value value-positive">${(account.totals?.inflow || 0).toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Total Outflow:</span>
                    <span className="value value-negative">${(account.totals?.outflow || 0).toFixed(2)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Net Total:</span>
                    <span className={`value ${(account.totals?.net || 0) >= 0 ? 'value-positive' : 'value-negative'}`}>
                      ${(account.totals?.net || 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
