import React, { useState, useEffect, useMemo } from 'react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import './Tabs.css'

interface CategoryData {
  [category: string]: number
}

export const IncomeExpenseTab: React.FC = () => {
  const [categoryData, setCategoryData] = useState<CategoryData>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchCategoryData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/database/stats')
      if (!response.ok) {
        throw new Error('Failed to fetch category data')
      }
      const data = await response.json()
      // Use the category summary from database stats
      setCategoryData(data.category_summary || {})
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchCategoryData()
  }, [])

  const { totalIncome, totalExpense } = useMemo(() => {
    const values = Object.values(categoryData)
    const income = values.reduce((sum, val) => sum + (val > 0 ? val : 0), 0)
    const expense = values.reduce((sum, val) => sum + (val < 0 ? Math.abs(val) : 0), 0)
    return { totalIncome: income, totalExpense: expense }
  }, [categoryData])

  return (
    <div className="income-expense-tab">
      <div className="tab-header">
        <h2><span aria-hidden="true">💰</span> Income & Expense Report</h2>
        <p>Breakdown of income and expenses by category</p>
        <button className="btn btn-primary" onClick={fetchCategoryData} disabled={loading}>
          {loading && <span className="spinner" aria-hidden="true"></span>}
          {loading ? 'Loading...' : 'Refresh Report'}
        </button>
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading report...</div>
      ) : Object.keys(categoryData).length === 0 ? (
        <div className="no-data">
          <p>No category data found. Make sure the backend has loaded your transaction data.</p>
        </div>
      ) : (
        <>
          <div className="summary-cards">
            <div className="card income-card">
              <div className="card-label">Total Income</div>
              <div className="card-value value-positive">${totalIncome.toFixed(2)}</div>
            </div>
            <div className="card expense-card">
              <div className="card-label">Total Expenses</div>
              <div className="card-value value-negative">${totalExpense.toFixed(2)}</div>
            </div>
            <div className={`card net-card ${totalIncome - totalExpense >= 0 ? 'positive' : 'negative'}`}>
              <div className="card-label">Net Income/Expense</div>
              <div className={`card-value ${totalIncome - totalExpense >= 0 ? 'value-positive' : 'value-negative'}`}>
                ${(totalIncome - totalExpense).toFixed(2)}
              </div>
            </div>
          </div>

          <div className="category-breakdown-container">
            <CategoryBreakdown
              categoryTotals={categoryData}
              title="By Category"
              titleLevel="h3"
            />
          </div>
        </>
      )}
    </div>
  )
}
