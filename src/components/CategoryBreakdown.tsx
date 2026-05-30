import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
}

export function CategoryBreakdown({ categoryTotals }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Sort by amount descending
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10) // Top 10 categories

  const total = Object.values(categoryTotals).reduce((sum, val) => sum + val, 0)
  const maxAmount = Math.max(...Object.values(categoryTotals))

  return (
    <div className="category-breakdown">
      <h3>Top Spending Categories</h3>
      <ul className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = total > 0 ? (amount / total) * 100 : 0
          const barWidth = maxAmount > 0 ? (amount / maxAmount) * 100 : 0
          return (
            <li key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className="category-amount">${amount.toFixed(2)}</span>
              </div>
              <div className="category-bar-container">
                <div
                  className="category-bar"
                  role="meter"
                  aria-valuenow={amount}
                  aria-valuemin={0}
                  aria-valuemax={maxAmount}
                  aria-label={`${category} spending: $${amount.toFixed(
                    2
                  )} (${percentage.toFixed(1)}%)`}
                  style={{
                    width: `${barWidth}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total</div>
            </li>
          )
        })}
      </ul>
      <div className="category-footer">
        <div className="total-spending">
          <span>Total Spending:</span>
          <span className="total-amount">${total.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {Object.keys(categoryTotals).length} categories
        </div>
      </div>
    </div>
  )
}
