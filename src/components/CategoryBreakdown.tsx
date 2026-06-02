import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title: string
}

export function CategoryBreakdown({ categoryTotals, title }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Sort by absolute amount descending to show most impactful categories (income or expense)
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  // Use absolute total for percentage calculations to show relative magnitude
  const totalAbs = Object.values(categoryTotals).reduce((sum, val) => sum + Math.abs(val), 0)
  const maxAmountAbs = Math.max(...Object.values(categoryTotals).map(Math.abs))

  return (
    <div className="category-breakdown">
      <h3>{title}</h3>
      <div className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const amountAbs = Math.abs(amount)
          const percentage = totalAbs > 0 ? (amountAbs / totalAbs) * 100 : 0
          const type = amount >= 0 ? 'income' : 'expense'

          return (
            <div key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className={`category-amount ${amount >= 0 ? 'value-positive' : 'value-negative'}`}>
                  ${amountAbs.toFixed(2)}
                </span>
              </div>
              <div className="category-bar-container">
                <div
                  className={`category-bar ${amount >= 0 ? 'income-bar' : 'expense-bar'}`}
                  role="meter"
                  aria-valuenow={amountAbs}
                  aria-valuemin={0}
                  aria-valuemax={maxAmountAbs}
                  aria-label={`${category} ${type}: $${amountAbs.toFixed(2)} (${percentage.toFixed(1)}%)`}
                  style={{
                    width: maxAmountAbs > 0 ? `${(amountAbs / maxAmountAbs) * 100}%` : '0%',
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of absolute total</div>
            </div>
          )
        })}
      </div>
      <div className="category-footer">
        <div className="total-spending">
          <span>Magnitude Total:</span>
          <span className="total-amount">${totalAbs.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {Object.keys(categoryTotals).length} categories
        </div>
      </div>
    </div>
  )
}
