import React, { useState, useEffect } from 'react'
import './Tabs.css'

interface AccountInfo {
  name: string
  type: string
  path: string
  transaction_count: number
  first_transaction_date: string | null
  last_transaction_date: string | null
  current_balance_present: boolean
  current_balance_updated_at: string | null
  net_value: number
  needs_current_balance: boolean
  needs_transactions: boolean
}

interface Transaction {
  date: string
  payee: string
  category: string
  outflow: number
  inflow: number
  amount: number
  description: string
}

type FilterType = 'all' | 'needs-data'

export const AccountsTab: React.FC = () => {
  const [accounts, setAccounts] = useState<AccountInfo[]>([])
  const [filter, setFilter] = useState<FilterType>('all')
  const [expandedAccounts, setExpandedAccounts] = useState<Set<string>>(new Set())
  const [accountTransactions, setAccountTransactions] = useState<Record<string, Transaction[]>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAccounts = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/accounts/status')
      if (!response.ok) {
        throw new Error('Failed to fetch account status data')
      }
      const data = await response.json()
      setAccounts(data.accounts || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts()
  }, [])

  const toggleAccountExpansion = async (accountName: string) => {
    const newExpanded = new Set(expandedAccounts)
    if (newExpanded.has(accountName)) {
      newExpanded.delete(accountName)
    } else {
      newExpanded.add(accountName)
      // Fetch transactions if not already loaded
      if (!accountTransactions[accountName]) {
        try {
          const encodedName = encodeURIComponent(accountName)
          const response = await fetch(`http://localhost:8000/accounts/${encodedName}/transactions`)
          if (response.ok) {
            const data = await response.json()
            setAccountTransactions(prev => ({
              ...prev,
              [accountName]: data.transactions || []
            }))
          }
        } catch (err) {
          console.error('Failed to fetch transactions:', err)
        }
      }
    }
    setExpandedAccounts(newExpanded)
  }

  const accountsNeedingData = accounts.filter((account) => account.needs_current_balance || account.needs_transactions)
  const needsDataCount = accountsNeedingData.length
  const filteredAccounts = filter === 'needs-data'
    ? accountsNeedingData
    : accounts

  return (
    <div className="accounts-tab">
      <div className="tab-header">
        <h2><span aria-hidden="true">💳</span> Accounts</h2>
        <p>View all accounts and their transaction summary</p>
        <div className="accounts-header-actions">
          <button className="btn btn-primary" onClick={fetchAccounts} disabled={loading}>
            {loading && <span className="spinner" aria-hidden="true"></span>}
            {loading ? 'Loading...' : 'Refresh Accounts'}
          </button>
          <div className="accounts-filter">
            <button
              className={`btn btn-secondary ${filter === 'all' ? 'active-filter' : ''}`}
              onClick={() => setFilter('all')}
              disabled={loading}
              aria-pressed={filter === 'all'}
            >
              All Accounts
            </button>
            <button
              className={`btn btn-secondary ${filter === 'needs-data' ? 'active-filter' : ''}`}
              onClick={() => setFilter('needs-data')}
              disabled={loading}
              aria-pressed={filter === 'needs-data'}
            >
              Needs Data ({needsDataCount})
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading accounts...</div>
      ) : (
        <>
          <div className="accounts-summary">
            <div className="summary-item">
              <span>Total Accounts</span>
              <strong>{accounts.length}</strong>
            </div>
            <div className="summary-item">
              <span>Accounts needing data</span>
              <strong>{needsDataCount}</strong>
            </div>
          </div>

          {filter === 'all' && (
            <div className="needs-data-section">
              <div className="needs-data-header">
                <h3>Data needed</h3>
                <p>Accounts below still require either transaction history or a current balance file.</p>
              </div>
              {needsDataCount > 0 ? (
                <div className="needs-data-list">
                  {accountsNeedingData.map((account, idx) => (
                    <div key={idx} className="needs-data-item">
                      <span>{account.name}</span>
                      <span className={`needs-data-tag ${account.needs_transactions ? 'needs-transactions' : 'needs-balance'}`}>
                        {account.needs_transactions ? 'Transactions missing' : 'Balance missing'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="all-loaded-message">
                  All accounts have the required transaction and balance data loaded.
                </div>
              )}
            </div>
          )}

          <div className="accounts-grid">
            {filteredAccounts.length === 0 ? (
              <div className="no-data">
                <p>No accounts found matching the selected filter.</p>
                {filter !== 'all' && (
                  <button
                    className="btn btn-secondary"
                    onClick={() => setFilter('all')}
                  >
                    Show All Accounts
                  </button>
                )}
              </div>
            ) : (
              filteredAccounts.map((account, idx) => (
                <div key={idx} className={`account-card ${account.needs_current_balance || account.needs_transactions ? 'needs-data' : ''}`}>
                  <div className="account-header">
                    <h3>{account.name}</h3>
                    <div className="account-header-actions">
                      <span className={`status-badge ${account.needs_current_balance || account.needs_transactions ? 'status-warning' : 'status-success'}`}>
                        {account.needs_transactions
                          ? 'Needs transactions'
                          : account.needs_current_balance
                          ? 'Needs balance'
                          : 'Loaded'}
                      </span>
                      {account.transaction_count > 0 && (
                        <button
                          className="btn btn-secondary expand-btn"
                          onClick={() => toggleAccountExpansion(account.name)}
                          aria-expanded={expandedAccounts.has(account.name)}
                          aria-controls={`transactions-${account.name.replace(/\s+/g, '-').toLowerCase()}`}
                        >
                          {expandedAccounts.has(account.name) ? 'Collapse' : 'Expand'} Transactions
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="account-details">
                    <div className="detail-item">
                      <span className="label">Type:</span>
                      <span className="value">{account.type || 'Unknown'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Transactions:</span>
                      <span className="value">{account.transaction_count}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Date Range:</span>
                      <span className="value">{account.first_transaction_date || 'N/A'} to {account.last_transaction_date || 'N/A'}</span>
                    </div>
                    <div className="detail-item">
                      <span className="label">Current Balance:</span>
                      <span className={`value ${account.current_balance_present ? 'value-positive' : 'value-negative'}`}>
                        {account.current_balance_present ? `$${account.net_value.toFixed(2)}` : 'Missing'}
                      </span>
                    </div>
                    {account.current_balance_present && (
                      <div className="detail-item">
                        <span className="label">Balance as of:</span>
                        <span className="value">{account.current_balance_updated_at || 'Unknown'}</span>
                      </div>
                    )}
                  </div>
                  {expandedAccounts.has(account.name) && accountTransactions[account.name] && (
                    <div className="account-transactions" id={`transactions-${account.name.replace(/\s+/g, '-').toLowerCase()}`}>
                      <h4>Recent Transactions</h4>
                      <div className="transactions-table-container">
                        <table className="transactions-table">
                          <thead>
                            <tr>
                              <th>Date</th>
                              <th>Payee</th>
                              <th>Category</th>
                              <th>Outflow</th>
                              <th>Inflow</th>
                              <th>Amount</th>
                            </tr>
                          </thead>
                          <tbody>
                            {accountTransactions[account.name].map((transaction, tIdx) => (
                              <tr key={tIdx}>
                                <td>{transaction.date}</td>
                                <td>{transaction.payee}</td>
                                <td>{transaction.category}</td>
                                <td className="value-negative">${transaction.outflow.toFixed(2)}</td>
                                <td className="value-positive">${transaction.inflow.toFixed(2)}</td>
                                <td className={`value ${transaction.amount >= 0 ? 'value-positive' : 'value-negative'}`}>
                                  ${transaction.amount.toFixed(2)}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
