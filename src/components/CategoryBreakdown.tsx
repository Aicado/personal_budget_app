import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
  titleLevel?: 'h2' | 'h3' | 'h4'
}

export function CategoryBreakdown({
  categoryTotals,
  title = 'Top Spending Categories',
  titleLevel = 'h3',
}: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Filter for expenses (negative values) and use absolute amounts
  const expenses = Object.entries(categoryTotals)
    .filter(([, amount]) => amount < 0)
    .map(([category, amount]) => [category, Math.abs(amount)] as [string, number])

  if (expenses.length === 0) return null

  // Sort by amount descending
  const sortedCategories = expenses.sort(([, a], [, b]) => b - a).slice(0, 10) // Top 10 categories

  const total = expenses.reduce((sum, [, val]) => sum + val, 0)
  const maxAmount = Math.max(...expenses.map(([, val]) => val))

  const TitleTag = titleLevel

  return (
    <div className="category-breakdown">
      <TitleTag>{title}</TitleTag>
      <div className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = (amount / total) * 100
          return (
            <div key={category} className="category-item">
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
                  aria-label={`${category} spending: $${amount.toFixed(2)}`}
                  style={{
                    width: `${(amount / maxAmount) * 100}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total spending</div>
            </div>
          )
        })}
      </div>
      <div className="category-footer">
        <div className="total-spending">
          <span>Total Spending:</span>
          <span className="total-amount">${total.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {expenses.length} spending categories
        </div>
      </div>
    </div>
  )
}
