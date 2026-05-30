import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
}

export function CategoryBreakdown({ categoryTotals }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Calculate total absolute spending for percentage calculations
  const totalAbs = Object.values(categoryTotals).reduce((sum, val) => sum + Math.abs(val), 0)

  // Sort by absolute amount descending
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  const maxAbsAmount = Math.max(...Object.values(categoryTotals).map(Math.abs))

  return (
    <div className="category-breakdown">
      <h4>Top Spending Categories</h4>
      <ul className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const absAmount = Math.abs(amount)
          const percentage = totalAbs > 0 ? (absAmount / totalAbs) * 100 : 0
          const isExpense = amount < 0
          const typeLabel = isExpense ? 'expense' : 'income'

          return (
            <li key={category} className="category-item">
              <div className="category-header" aria-hidden="true">
                <span className="category-name">{category}</span>
                <span className={`category-amount ${isExpense ? 'expense' : 'income'}`}>
                  ${absAmount.toFixed(2)}
                </span>
              </div>
              <div className="category-bar-container">
                <div
                  className={`category-bar ${isExpense ? 'expense-bar' : 'income-bar'}`}
                  role="meter"
                  aria-valuenow={absAmount}
                  aria-valuemin={0}
                  aria-valuemax={maxAbsAmount}
                  aria-label={`${category} ${typeLabel}: $${absAmount.toFixed(2)} (${percentage.toFixed(1)}%)`}
                  style={{
                    width: `${maxAbsAmount > 0 ? (absAmount / maxAbsAmount) * 100 : 0}%`,
                  }}
                />
              </div>
              <div className="category-percentage" aria-hidden="true">
                {percentage.toFixed(1)}% of total
              </div>
            </li>
          )
        })}
      </ul>
      <div className="category-footer">
        <div className="total-spending">
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
