import './SummaryStats.css'

interface SummaryStatsProps {
  stats: {
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

export function SummaryStats({ stats }: SummaryStatsProps) {
  return (
    <div className="summary-stats">
      <h2>Summary Statistics</h2>
      <div className="stats-grid">
        <div className="stat-card income">
          <div className="stat-icon">📈</div>
          <div className="stat-label">Total Income</div>
          <div className="stat-value">${stats.total_inflow.toFixed(2)}</div>
        </div>
        <div className="stat-card expense">
          <div className="stat-icon">📉</div>
          <div className="stat-label">Total Expenses</div>
          <div className="stat-value">${stats.total_outflow.toFixed(2)}</div>
        </div>
        <div className={`stat-card net ${stats.net_total >= 0 ? 'positive' : 'negative'}`}>
          <div className="stat-icon">{stats.net_total >= 0 ? '✅' : '⚠️'}</div>
          <div className="stat-label">Net Total</div>
          <div className="stat-value">${stats.net_total.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-label">Avg Monthly Income</div>
          <div className="stat-value">${stats.avg_monthly_inflow.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📋</div>
          <div className="stat-label">Avg Monthly Expenses</div>
          <div className="stat-value">${stats.avg_monthly_outflow.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🏷️</div>
          <div className="stat-label">Categories</div>
          <div className="stat-value">{stats.unique_categories}</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-label">Transactions</div>
          <div className="stat-value">{stats.transaction_count}</div>
        </div>
        <div className="stat-card date-range">
          <div className="stat-icon">📅</div>
          <div className="stat-label">Date Range</div>
          <div className="stat-value-small">
            {stats.date_range.start} to {stats.date_range.end}
          </div>
        </div>
      </div>
    </div>
  )
}
