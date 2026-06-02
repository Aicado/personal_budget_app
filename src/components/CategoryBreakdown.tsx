import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
}

export function CategoryBreakdown({ categoryTotals, title = 'Top Categories' }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Sort by absolute amount descending to show most significant categories first
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  // Calculate total absolute volume for percentage calculation
  const totalAbs = Object.values(categoryTotals).reduce((sum, val) => sum + Math.abs(val), 0)
  // Calculate max absolute amount for bar scaling
  const maxAbs = Math.max(...Object.values(categoryTotals).map(Math.abs))

  return (
    <div className="category-breakdown">
      <h3>{title}</h3>
      <div className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const isExpense = amount < 0
          const absAmount = Math.abs(amount)
          const percentage = totalAbs > 0 ? (absAmount / totalAbs) * 100 : 0

          return (
            <div key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className={`category-amount ${isExpense ? 'value-negative' : 'value-positive'}`}>
                  ${absAmount.toFixed(2)}
                </span>
              </div>
              <div className="category-bar-container">
                <div
                  className={`category-bar ${isExpense ? 'expense-bar' : 'income-bar'}`}
                  role="meter"
                  aria-valuenow={absAmount}
                  aria-valuemin={0}
                  aria-valuemax={maxAbs}
                  aria-label={`${category} ${isExpense ? 'expense' : 'income'}: $${absAmount.toFixed(2)} (${percentage.toFixed(1)}%)`}
                  style={{
                    width: `${maxAbs > 0 ? (absAmount / maxAbs) * 100 : 0}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total volume</div>
            </div>
          )
        })}
      </div>
      <div className="category-footer">
        <div className="total-volume">
          <span>Total Volume:</span>
          <span className="total-amount">${totalAbs.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {Object.keys(categoryTotals).length} categories
        </div>
      </div>
    </div>
  )
}
