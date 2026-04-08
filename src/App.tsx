import { useState } from 'react'
import './App.css'
import { FileUpload } from './components/FileUpload'
import { BackfillStatus } from './components/BackfillStatus'
import { UploadTab } from './components/tabs/UploadTab'
import { BackfillTab } from './components/tabs/BackfillTab'
import { AccountsTab } from './components/tabs/AccountsTab'
import { IncomeExpenseTab } from './components/tabs/IncomeExpenseTab'
import { NetWorthTab } from './components/tabs/NetWorthTab'
import { SpendingTrendsTab } from './components/tabs/SpendingTrendsTab'

type TabType = 'upload' | 'backfill' | 'accounts' | 'income-expense' | 'net-worth' | 'spending-trends'

interface AnalysisResult {
  filename: string
  monthly_trends: {
    months: string[]
    net_amounts: number[]
    outflows: number[]
    inflows: number[]
  }
  category_trends: {
    months: string[]
    categories: string[]
    data: Record<string, number[]>
  }
  category_totals: Record<string, number>
  summary_stats: {
    total_inflow: number
    total_outflow: number
    net_total: number
    avg_monthly_inflow: number
    avg_monthly_outflow: number
    transaction_count: number
    unique_categories: number
    date_range: {
      start: string
      end: string
    }
  }
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('upload')
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)

  const tabs: Array<{ id: TabType; label: string; icon: string }> = [
    { id: 'upload', label: 'Upload CSV', icon: '📤' },
    { id: 'backfill', label: 'Backfill Database', icon: '📥' },
    { id: 'accounts', label: 'Accounts', icon: '💳' },
    { id: 'income-expense', label: 'Income/Expense', icon: '💰' },
    { id: 'net-worth', label: 'Net Worth', icon: '📊' },
    { id: 'spending-trends', label: 'Spending Trends', icon: '📈' },
  ]

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>📊 YNAB Transaction Analyzer</h1>
          <p className="subtitle">Upload your YNAB export files to visualize spending trends</p>
        </div>
      </header>

      <div className="tabs-container">
        <nav className="tabs-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </nav>

        <main className="app-main">
          {activeTab === 'upload' && <UploadTab onAnalysisComplete={setAnalysisData} />}
          {activeTab === 'backfill' && <BackfillTab />}
          {activeTab === 'accounts' && <AccountsTab />}
          {activeTab === 'income-expense' && <IncomeExpenseTab />}
          {activeTab === 'net-worth' && <NetWorthTab />}
          {activeTab === 'spending-trends' && <SpendingTrendsTab />}
        </main>
      </div>

      <footer className="app-footer">
        <p>💡 Tip: You can upload one or multiple YNAB transaction export CSV files</p>
      </footer>
    </div>
  )
}

export default App
