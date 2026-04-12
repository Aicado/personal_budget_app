import React, { useState, useEffect } from 'react'
import './DashboardHome.css'

interface Period {
  label: string
  income: number
  expense: number
  net: number
}

export const DashboardHome: React.FC = () => {
  const [periods, setPeriods] = useState<Period[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [totalBalance, setTotalBalance] = useState(0)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Fetch monthly trends and account balances
      const response = await fetch('http://localhost:8000/database/stats')
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard data')
      }
      const data = await response.json()

      // Fetch account balances for net worth
      const accountsResponse = await fetch('http://localhost:8000/accounts/status')
      if (accountsResponse.ok) {
        const accountsData = await accountsResponse.json()
        const balance = accountsData.accounts.reduce((sum: number, acc: any) => sum + acc.net_value, 0)
        setTotalBalance(balance)
      }

      // Process monthly data
      const monthlyTrends = data.monthly_trends || {}
      const months = monthlyTrends.months || []
      const inflows = monthlyTrends.inflows || []
      const outflows = monthlyTrends.outflows || []

      // Calculate periods
      const now = new Date()
      const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
      const lastMonth = getMonthOffset(now, -1)
      const currentYear = `${now.getFullYear()}`
      const lastYear = `${now.getFullYear() - 1}`

      const periodData: Period[] = [
        {
          label: 'Current Month',
          ...getPeriodData(months, inflows, outflows, currentMonth, 'month')
        },
        {
          label: 'Last Month',
          ...getPeriodData(months, inflows, outflows, lastMonth, 'month')
        },
        {
          label: 'Current Year',
          ...getPeriodData(months, inflows, outflows, currentYear, 'year')
        },
        {
          label: 'Last Year',
          ...getPeriodData(months, inflows, outflows, lastYear, 'year')
        }
      ]

      setPeriods(periodData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard')
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  const getMonthOffset = (date: Date, offset: number): string => {
    const d = new Date(date)
    d.setMonth(d.getMonth() + offset)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  }

  const getPeriodData = (
    months: string[],
    inflows: number[],
    outflows: number[],
    period: string,
    type: 'month' | 'year'
  ): { income: number; expense: number; net: number } => {
    let totalIncome = 0
    let totalExpense = 0

    months.forEach((month, idx) => {
      const matches = type === 'month' ? month === period : month.startsWith(period)
      if (matches) {
        totalIncome += inflows[idx] || 0
        totalExpense += outflows[idx] || 0
      }
    })

    return {
      income: totalIncome,
      expense: totalExpense,
      net: totalIncome - totalExpense
    }
  }

  if (loading) {
    return (
      <div className="dashboard-home loading-state">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard-home">
      <div className="dashboard-header">
        <h1>📊 Dashboard</h1>
        <p>Overview of your income and expenses</p>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button className="btn btn-small" onClick={fetchDashboardData}>Retry</button>
        </div>
      )}

      {/* Net Worth Summary */}
      <div className="net-worth-card">
        <h2>Current Net Worth</h2>
        <p className={`net-worth-value ${totalBalance >= 0 ? 'positive' : 'negative'}`}>
          ${totalBalance.toFixed(2)}
        </p>
      </div>

      {/* Period Cards */}
      <div className="periods-grid">
        {periods.map((period, idx) => (
          <div key={idx} className="period-card">
            <h3>{period.label}</h3>
            <div className="period-stats">
              <div className="stat">
                <label>Income</label>
                <p className="value positive">${period.income.toFixed(2)}</p>
              </div>
              <div className="stat">
                <label>Expense</label>
                <p className="value negative">${period.expense.toFixed(2)}</p>
              </div>
              <div className="stat divider">
                <label>Net</label>
                <p className={`value ${period.net >= 0 ? 'positive' : 'negative'}`}>
                  ${period.net.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="refresh-section">
        <button className="btn btn-primary" onClick={fetchDashboardData} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Dashboard'}
        </button>
      </div>
    </div>
  )
}
