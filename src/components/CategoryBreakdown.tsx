import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
}

export function CategoryBreakdown({ categoryTotals }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Sort by magnitude descending
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  const total = Object.values(categoryTotals).reduce((sum, val) => sum + Math.abs(val), 0)
  const maxAmount = Math.max(...Object.values(categoryTotals).map(v => Math.abs(v)))

  return (
    <div className="category-breakdown">
      <h3>Top Spending Categories</h3>
      <div
        className="categories-list"
        tabIndex={0}
        role="region"
        aria-label="Categories spending breakdown"
      >
        {sortedCategories.map(([category, amount]) => {
          const absAmount = Math.abs(amount)
          const percentage = (absAmount / total) * 100
          return (
            <div key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className="category-amount">${absAmount.toFixed(2)}</span>
              </div>
              <div className="category-bar-container">
                <div
                  className="category-bar"
                  role="meter"
                  aria-valuenow={absAmount}
                  aria-valuemin={0}
                  aria-valuemax={maxAmount}
                  aria-label={`${category} spending: $${absAmount.toFixed(2)}`}
                  style={{
                    width: `${(absAmount / maxAmount) * 100}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total</div>
            </div>
          )
        })}
      </div>
      <div className="category-footer">
        <div className="total-spending">
          <span>Total Spending:</span>
          <span className="total-amount value-negative">${total.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {Object.keys(categoryTotals).length} categories
        </div>
      </div>
    </div>
  )
}
