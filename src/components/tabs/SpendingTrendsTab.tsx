import React, { useState, useEffect } from 'react'
import { MonthlySummary } from '../MonthlySummary'
import './Tabs.css'

interface MonthlyTrend {
  months: string[]
  net_amounts: number[]
  outflows: number[]
  inflows: number[]
}

export const SpendingTrendsTab: React.FC = () => {
  const [trendsData, setTrendsData] = useState<MonthlyTrend | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTrendsData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/database/stats')
      if (!response.ok) {
        throw new Error('Failed to fetch trends data')
      }
      const data = await response.json()
      
      const trends = data.monthly_trends || {
        months: [],
        net_amounts: [],
        outflows: [],
        inflows: []
      }
      setTrendsData(trends)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTrendsData()
  }, [])

  return (
    <div className="spending-trends-tab">
      <div className="tab-header">
        <h2><span aria-hidden="true">📈</span> Spending Trends</h2>
        <p>Analyze your income and spending patterns over time</p>
        <button className="btn btn-primary" onClick={fetchTrendsData} disabled={loading}>
          {loading && <span className="spinner" aria-hidden="true"></span>}
          {loading ? 'Loading...' : 'Refresh Trends'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading ? (
        <div className="loading">Loading spending trends...</div>
      ) : trendsData ? (
        <>
          <div className="trends-summary">
            <div className="trend-card">
              <div className="trend-label">Average Monthly Income</div>
              <div className="trend-value value-positive">
                ${(trendsData.inflows.reduce((a, b) => a + b, 0) / trendsData.inflows.length).toFixed(2)}
              </div>
            </div>
            <div className="trend-card">
              <div className="trend-label">Average Monthly Spending</div>
              <div className="trend-value value-negative">
                ${(trendsData.outflows.reduce((a, b) => a + b, 0) / trendsData.outflows.length).toFixed(2)}
              </div>
            </div>
            <div className="trend-card">
              <div className="trend-label">Average Net Monthly</div>
              <div className="trend-value value-positive">
                ${(trendsData.net_amounts.reduce((a, b) => a + b, 0) / trendsData.net_amounts.length).toFixed(2)}
              </div>
            </div>
          </div>

          <div className="trends-chart">
            <MonthlySummary
              months={trendsData.months}
              inflows={trendsData.inflows}
              outflows={trendsData.outflows}
              netAmounts={trendsData.net_amounts}
            />
          </div>

          <div className="trends-detail">
            <h3>Monthly Details</h3>
            <table className="trends-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Inflow</th>
                  <th>Outflow</th>
                  <th>Net</th>
                </tr>
              </thead>
              <tbody>
                {trendsData.months.map((month, idx) => (
                  <tr key={idx}>
                    <td>{month}</td>
                    <td className="value-positive">${trendsData.inflows[idx].toFixed(2)}</td>
                    <td className="value-negative">${trendsData.outflows[idx].toFixed(2)}</td>
                    <td className={trendsData.net_amounts[idx] >= 0 ? 'value-positive' : 'value-negative'}>
                      ${trendsData.net_amounts[idx].toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <div className="no-data">
          <p>No spending trends data available. Make sure the backend has loaded the data directory.</p>
        </div>
      )}
    </div>
  )
}
