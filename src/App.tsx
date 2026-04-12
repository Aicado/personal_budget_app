import { useState } from 'react'
import './App.css'
import { Sidebar } from './components/Sidebar'
import { DashboardHome } from './components/DashboardHome'
import { AllTransactionsPage } from './components/AllTransactionsPage'
import { AccountDetail } from './components/AccountDetail'

type PageType = 'dashboard' | 'transactions' | 'account'

function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('dashboard')
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)

  const handleNavigate = (page: string, account?: string) => {
    const pageType = page as PageType
    setCurrentPage(pageType)
    if (pageType === 'account' && account) {
      setSelectedAccount(account)
    } else if (pageType === 'dashboard' || pageType === 'transactions') {
      setSelectedAccount(null)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>📊 Personal Budget App</h1>
          <p className="subtitle">Automatically load account and transaction data from the backend data store</p>
        </div>
      </header>

      <div className="app-container">
        <Sidebar 
          currentPage={currentPage} 
          selectedAccount={selectedAccount}
          onNavigate={handleNavigate}
        />

        <main className="app-main">
          {currentPage === 'dashboard' && <DashboardHome />}
          {currentPage === 'transactions' && <AllTransactionsPage />}
          {currentPage === 'account' && selectedAccount && (
            <AccountDetail 
              accountName={selectedAccount}
              onBack={() => handleNavigate('dashboard')}
            />
          )}
        </main>
      </div>

      <footer className="app-footer">
        <p>💡 Tip: Account and transaction data are loaded automatically from the backend data directory.</p>
      </footer>
    </div>
  )
}

export default App
