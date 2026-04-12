import React, { useState, useEffect } from 'react'
import './Sidebar.css'

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

interface SidebarProps {
  currentPage: string
  selectedAccount: string | null
  onNavigate: (page: string, account?: string) => void
}

type AccountsByType = Record<string, AccountInfo[]>

export const Sidebar: React.FC<SidebarProps> = ({ currentPage, selectedAccount, onNavigate }) => {
  const [accounts, setAccounts] = useState<AccountInfo[]>([])
  const [expandedTypes, setExpandedTypes] = useState<Set<string>>(new Set(['checkings', 'credit_cards', 'investments', 'savings', 'assets']))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/accounts/status')
      if (!response.ok) {
        throw new Error('Failed to fetch accounts')
      }
      const data = await response.json()
      setAccounts(data.accounts || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching accounts:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleAccountType = (type: string) => {
    const newExpanded = new Set(expandedTypes)
    if (newExpanded.has(type)) {
      newExpanded.delete(type)
    } else {
      newExpanded.add(type)
    }
    setExpandedTypes(newExpanded)
  }

  const groupAccountsByType = (accountlist: AccountInfo[]): AccountsByType => {
    const grouped: AccountsByType = {}
    accountlist.forEach(account => {
      // Normalize the account type for grouping
      const typeNormalized = account.type.toLowerCase().replace(/\s+/g, '_')
      if (!grouped[typeNormalized]) {
        grouped[typeNormalized] = []
      }
      grouped[typeNormalized].push(account)
    })
    // Sort accounts within each type by name
    Object.keys(grouped).forEach(type => {
      grouped[type].sort((a, b) => a.name.localeCompare(b.name))
    })
    return grouped
  }

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      'checkings': 'Checking Accounts',
      'credit_cards': 'Credit Cards',
      'investments': 'Investments',
      'savings': 'Savings Accounts',
      'assets': 'Assets',
    }
    return labels[type] || type
  }

  const getTypeIcon = (type: string): string => {
    const icons: Record<string, string> = {
      'checkings': '🏦',
      'credit_cards': '💳',
      'investments': '📈',
      'savings': '💰',
      'assets': '🏠',
    }
    return icons[type] || '📊'
  }

  const accountsByType = groupAccountsByType(accounts)
  const typeOrder = ['checkings', 'credit_cards', 'investments', 'savings', 'assets']
  const sortedTypes = typeOrder.filter(t => t in accountsByType)

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>Personal Budget</h2>
        <p className="sidebar-subtitle">Accounts</p>
      </div>

      {error && (
        <div className="sidebar-error">
          <p>{error}</p>
          <button className="btn-small" onClick={fetchAccounts}>Retry</button>
        </div>
      )}

      <nav className="sidebar-nav">
        {/* Home Link */}
        <div className="nav-section">
          <button
            className={`nav-home ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => onNavigate('home')}
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-label">Home</span>
            <span className="nav-description">All Transactions</span>
          </button>
        </div>

        {/* Account Groups */}
        <div className="nav-section">
          {loading ? (
            <div className="sidebar-loading">Loading accounts...</div>
          ) : sortedTypes.length > 0 ? (
            sortedTypes.map(type => (
              <div key={type} className="account-group">
                <button
                  className="group-header"
                  onClick={() => toggleAccountType(type)}
                >
                  <span className="group-icon">{getTypeIcon(type)}</span>
                  <span className="group-label">{getTypeLabel(type)}</span>
                  <span className={`group-toggle ${expandedTypes.has(type) ? 'expanded' : ''}`}>▶</span>
                  <span className="group-count">{accountsByType[type].length}</span>
                </button>

                {expandedTypes.has(type) && (
                  <div className="group-accounts">
                    {accountsByType[type].map(account => (
                      <button
                        key={account.name}
                        className={`account-item ${selectedAccount === account.name ? 'active' : ''}`}
                        onClick={() => onNavigate('account', account.name)}
                      >
                        <span className="account-name">{account.name}</span>
                        <span className={`account-balance ${account.net_value >= 0 ? 'positive' : 'negative'}`}>
                          ${account.net_value.toFixed(0)}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="sidebar-empty">No accounts found</div>
          )}
        </div>
      </nav>

      <div className="sidebar-footer">
        <button className="btn-small" onClick={fetchAccounts} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>
    </aside>
  )
}
