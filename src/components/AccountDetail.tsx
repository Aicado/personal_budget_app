import React, { useState, useEffect } from 'react'
import './AccountDetail.css'

interface Transaction {
  date: string
  payee: string
  category: string
  outflow: number
  inflow: number
  amount: number
  description: string
}

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

interface AccountDetailProps {
  accountName: string
  onBack: () => void
}

export const AccountDetail: React.FC<AccountDetailProps> = ({ accountName, onBack }) => {
  const [account, setAccount] = useState<AccountInfo | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAccountData()
  }, [accountName])

  const fetchAccountData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch account details
      const accountResponse = await fetch('http://localhost:8000/accounts/status')
      if (!accountResponse.ok) {
        throw new Error('Failed to fetch account status')
      }
      const accountData = await accountResponse.json()
      const accounts = accountData.accounts || []
      const foundAccount = accounts.find((a: AccountInfo) => a.name === accountName)
      
      if (!foundAccount) {
        throw new Error(`Account ${accountName} not found`)
      }
      
      setAccount(foundAccount)

      // Fetch transactions for this account
      const encodedName = encodeURIComponent(accountName)
      const transResponse = await fetch(`http://localhost:8000/accounts/${encodedName}/transactions`)
      if (!transResponse.ok) {
        throw new Error('Failed to fetch transactions')
      }
      const transData = await transResponse.json()
      setTransactions(transData.transactions || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load account data')
      console.error('Error fetching account data:', err)
    } finally {
      setLoading(false)
    }
  }

  const sortedTransactions = [...transactions].sort((a, b) => {
    const dateA = new Date(a.date).getTime()
    const dateB = new Date(b.date).getTime()
    return dateB - dateA // Most recent first
  })

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'checkings': '🏦 Checking Account',
      'credit_cards': '💳 Credit Card',
      'investments': '📈 Investment',
      'savings': '💰 Savings Account',
      'assets': '🏠 Asset',
    }
    return labels[type] || type
  }

  const calculateStats = () => {
    let totalInflow = 0
    let totalOutflow = 0

    transactions.forEach(t => {
      totalInflow += t.inflow
      totalOutflow += t.outflow
    })

    return { totalInflow, totalOutflow }
  }

  const stats = calculateStats()

  if (loading) {
    return (
      <div className="account-detail loading-state">
        <div className="spinner"></div>
        <p>Loading account details...</p>
      </div>
    )
  }

  if (!account) {
    return (
      <div className="account-detail error-state">
        <p>Account not found</p>
        <button className="btn btn-primary" onClick={onBack}>Back to Home</button>
      </div>
    )
  }

  return (
    <div className="account-detail">
      <div className="account-detail-header">
        <button className="btn-back" onClick={onBack}>← Back</button>
        <div className="header-content">
          <h1>{account.name}</h1>
          <p className="account-type">{getTypeLabel(account.type)}</p>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button className="btn btn-small" onClick={fetchAccountData}>Retry</button>
        </div>
      )}

      {/* Account Summary Cards */}
      <div className="account-summary">
        <div className="summary-card">
          <h3>Current Balance</h3>
          <p className={`summary-value ${account.net_value >= 0 ? 'positive' : 'negative'}`}>
            ${account.net_value.toFixed(2)}
          </p>
          {account.current_balance_updated_at && (
            <p className="summary-detail">as of {account.current_balance_updated_at}</p>
          )}
        </div>

        <div className="summary-card">
          <h3>Total Transactions</h3>
          <p className="summary-value">{account.transaction_count}</p>
        </div>

        <div className="summary-card">
          <h3>Total Inflow</h3>
          <p className="summary-value positive">${stats.totalInflow.toFixed(2)}</p>
        </div>

        <div className="summary-card">
          <h3>Total Outflow</h3>
          <p className="summary-value negative">${stats.totalOutflow.toFixed(2)}</p>
        </div>

        <div className="summary-card">
          <h3>Date Range</h3>
          <p className="summary-value">
            {account.first_transaction_date ? account.first_transaction_date : 'N/A'} to {account.last_transaction_date ? account.last_transaction_date : 'N/A'}
          </p>
        </div>
      </div>

      {/* Transactions Table */}
      <div className="transactions-section">
        <h2>Transactions</h2>
        
        {sortedTransactions.length === 0 ? (
          <div className="empty-state">
            <p>No transactions found for this account</p>
          </div>
        ) : (
          <div className="transactions-container">
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
                {sortedTransactions.map((transaction, idx) => (
                  <tr key={idx}>
                    <td className="date-cell">{transaction.date}</td>
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
