import { useState } from 'react'
import './App.css'
import { AccountsTab } from './components/tabs/AccountsTab'
import { IncomeExpenseTab } from './components/tabs/IncomeExpenseTab'
import { NetWorthTab } from './components/tabs/NetWorthTab'
import { SpendingTrendsTab } from './components/tabs/SpendingTrendsTab'

type TabType = 'accounts' | 'income-expense' | 'net-worth' | 'spending-trends'

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('accounts')

  const tabs: Array<{ id: TabType; label: string; icon: string }> = [
    { id: 'accounts', label: 'Accounts', icon: '💳' },
    { id: 'income-expense', label: 'Income/Expense', icon: '💰' },
    { id: 'net-worth', label: 'Net Worth', icon: '📊' },
    { id: 'spending-trends', label: 'Spending Trends', icon: '📈' },
  ]

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>
            <span aria-hidden="true">📊</span> Personal Budget App
          </h1>
          <p className="subtitle">Automatically load account and transaction data from the backend data store</p>
        </div>
      </header>

      <div className="tabs-container">
        <nav className="tabs-nav" role="tablist" aria-label="Main navigation" role="tablist" aria-label="Dashboard sections">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              id={`${tab.id}-tab`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`${tab.id}-panel`}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
            >
              <span className="tab-icon" aria-hidden="true">
                {tab.icon}
              </span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </nav>

        <main className="app-main">
          <div
            key={activeTab}
            id={`panel-${activeTab}`}
            role="tabpanel"
            aria-labelledby={`tab-${activeTab}`}
            className="results-section"
          >
            <div
            id={`${activeTab}-panel`}
            role="tabpanel"
            aria-labelledby={`${activeTab}-tab`}
            tabIndex={0}
          >
            {activeTab === 'accounts' && <AccountsTab />}
              {activeTab === 'income-expense' && <IncomeExpenseTab />}
              {activeTab === 'net-worth' && <NetWorthTab />}
              {activeTab === 'spending-trends' && <SpendingTrendsTab />}
          </div>
          </div>
        </main>
      </div>

      <footer className="app-footer">
        <p>💡 Tip: Account and transaction data are loaded automatically from the backend data directory.</p>
      </footer>
    </div>
  )
}

export default App
