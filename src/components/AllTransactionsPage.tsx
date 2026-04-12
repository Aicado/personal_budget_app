import React, { useState, useEffect } from 'react'
import './HomePage.css'

interface Transaction {
  date: string
  payee: string
  category: string
  outflow: number
  inflow: number
  amount: number
  description: string
  account: string
  account_type: string
}

interface AccountInfo {
  name: string
  type: string
  net_value: number
}

interface DuplicateMap {
  [key: string]: number
}

export const AllTransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [accounts, setAccounts] = useState<AccountInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [duplicateMap, setDuplicateMap] = useState<DuplicateMap>({})
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch accounts for summary
      const accountsResponse = await fetch('http://localhost:8000/accounts/status')
      if (!accountsResponse.ok) {
        throw new Error('Failed to fetch accounts')
      }
      const accountsData = await accountsResponse.json()
      const accountsList = accountsData.accounts || []
      setAccounts(accountsList)

      // Fetch all transactions - try the transactions endpoint
      // First, check if there's a dedicated endpoint, otherwise fetch from each account
      let allTransactions: Transaction[] = []
      
      try {
        const transResponse = await fetch('http://localhost:8000/database/transactions')
        if (transResponse.ok) {
          const transData = await transResponse.json()
          allTransactions = transData.transactions || []
        }
      } catch (err) {
        // If that fails, fetch from each account
        console.log('Fetching transactions per account...')
        for (const account of accountsList) {
          try {
            const encodedName = encodeURIComponent(account.name)
            const response = await fetch(`http://localhost:8000/accounts/${encodedName}/transactions`)
            if (response.ok) {
              const data = await response.json()
              const accountTransactions = (data.transactions || []).map((t: Transaction) => ({
                ...t,
                account: account.name,
                account_type: account.type,
              }))
              allTransactions.push(...accountTransactions)
            }
          } catch (err) {
            console.error(`Failed to fetch transactions for ${account.name}:`, err)
          }
        }
      }

      setTransactions(allTransactions)
      detectDuplicates(allTransactions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data')
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const detectDuplicates = (transactionsList: Transaction[]) => {
    const duplicates: DuplicateMap = {}
    
    // Group by (date, payee, amount, account) to find duplicates
    const groupMap: Record<string, Transaction[]> = {}
    
    transactionsList.forEach((transaction) => {
      const key = `${transaction.date}|${transaction.payee}|${transaction.amount.toFixed(2)}|${transaction.account}`
      if (!groupMap[key]) {
        groupMap[key] = []
      }
      groupMap[key].push(transaction)
    })

    // Mark duplicates
    Object.keys(groupMap).forEach(key => {
      if (groupMap[key].length > 1) {
        groupMap[key].forEach((_, idx) => {
          const txKey = `${key}|${idx}`
          duplicates[txKey] = groupMap[key].length
        })
      }
    })

    setDuplicateMap(duplicates)
  }

  const getTotalBalance = (): number => {
    return accounts.reduce((sum, acc) => sum + acc.net_value, 0)
  }

  const filteredTransactions = selectedAccount
    ? transactions.filter(t => t.account === selectedAccount)
    : transactions

  const sortedTransactions = [...filteredTransactions].sort((a, b) => {
    const dateA = new Date(a.date).getTime()
    const dateB = new Date(b.date).getTime()
    return dateB - dateA // Most recent first
  })

  return (
    <div className="home-page">
      <div className="home-header">
        <h1>💱 Transactions</h1>
        <p>View all transactions across your accounts</p>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button className="btn btn-small" onClick={fetchData}>Retry</button>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading transactions...</p>
        </div>
      ) : (
        <>
          {/* Balance Summary */}
          <div className="balance-summary">
            <div className="summary-card">
              <h3>Total Net Worth</h3>
              <p className={`summary-value ${getTotalBalance() >= 0 ? 'positive' : 'negative'}`}>
                ${getTotalBalance().toFixed(2)}
              </p>
            </div>
            <div className="summary-card">
              <h3>Total Accounts</h3>
              <p className="summary-value">{accounts.length}</p>
            </div>
            <div className="summary-card">
              <h3>Total Transactions</h3>
              <p className="summary-value">{sortedTransactions.length}</p>
            </div>
            <div className="summary-card">
              <h3>Potential Duplicates</h3>
              <p className="summary-value warning">{Object.keys(duplicateMap).length}</p>
            </div>
          </div>

          {/* Account Filter */}
          <div className="account-filter">
            <label htmlFor="account-select">Filter by Account:</label>
            <select
              id="account-select"
              value={selectedAccount || ''}
              onChange={(e) => setSelectedAccount(e.target.value || null)}
            >
              <option value="">All Accounts</option>
              {accounts.map(account => (
                <option key={account.name} value={account.name}>
                  {account.name} (${account.net_value.toFixed(0)})
                </option>
              ))}
            </select>
          </div>

          {/* Transactions Table */}
          <div className="transactions-section">
            <h2>Transactions {selectedAccount && `- ${selectedAccount}`}</h2>
            
            {sortedTransactions.length === 0 ? (
              <div className="empty-state">
                <p>No transactions found</p>
              </div>
            ) : (
              <div className="transactions-container">
                <table className="transactions-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Account</th>
                      <th>Payee</th>
                      <th>Category</th>
                      <th>Outflow</th>
                      <th>Inflow</th>
                      <th>Amount</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedTransactions.map((transaction, idx) => {
                      const isDuplicate = Object.keys(duplicateMap).some(key => {
                        const keyParts = key.split('|')
                        return keyParts[0] === transaction.date &&
                               keyParts[1] === transaction.payee &&
                               keyParts[2] === transaction.amount.toFixed(2) &&
                               keyParts[3] === transaction.account
                      })
                      
                      return (
                        <tr key={idx} className={isDuplicate ? 'duplicate-row' : ''}>
                          <td className="date-cell">{transaction.date}</td>
                          <td className="account-cell">{transaction.account}</td>
                          <td className="payee-cell">{transaction.payee}</td>
                          <td className="category-cell">{transaction.category}</td>
                          <td className="value-cell negative">
                            {transaction.outflow > 0 ? `$${transaction.outflow.toFixed(2)}` : '-'}
                          </td>
                          <td className="value-cell positive">
                            {transaction.inflow > 0 ? `$${transaction.inflow.toFixed(2)}` : '-'}
                          </td>
                          <td className={`value-cell ${transaction.amount >= 0 ? 'positive' : 'negative'}`}>
                            ${transaction.amount.toFixed(2)}
                          </td>
                          <td className="status-cell">
                            {isDuplicate && (
                              <span className="duplicate-badge">⚠️ Duplicate</span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
