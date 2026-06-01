import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
  type?: 'income' | 'expense'
}

export function CategoryBreakdown({ categoryTotals, title, type = 'expense' }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Filter based on type (income: positive, expense: negative)
  const filteredEntries = Object.entries(categoryTotals).filter(([, amount]) => {
    if (type === 'income') return amount > 0
    return amount < 0
  })

  if (filteredEntries.length === 0) return null

  // Sort by absolute amount descending to show top impact
  const sortedCategories = filteredEntries
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  const totalAbs = filteredEntries.reduce((sum, [, val]) => sum + Math.abs(val), 0)
  const maxAbs = Math.max(...filteredEntries.map(([, val]) => Math.abs(val)))

  const defaultTitle = type === 'income' ? 'Top Income Categories' : 'Top Spending Categories'

  return (
    <div className="category-breakdown">
      <h3>{title || defaultTitle}</h3>
      <ul className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const absAmount = Math.abs(amount)
          const percentage = totalAbs > 0 ? (absAmount / totalAbs) * 100 : 0
          return (
            <li key={category} className="category-item">
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
                  aria-valuemax={maxAbs}
                  aria-label={`${category} ${type}: $${absAmount.toFixed(2)} (${percentage.toFixed(1)}%)`}
                  style={{
                    width: `${maxAbs > 0 ? (absAmount / maxAbs) * 100 : 0}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total {type}</div>
            </li>
          )
        })}
      </ul>
      <div className="category-footer">
        <div className="total-spending">
          <span>Total {type === 'income' ? 'Income' : 'Spending'}:</span>
          <span className="total-amount">${totalAbs.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {filteredEntries.length} {type} categories
        </div>
      </div>
    </div>
  )
}
