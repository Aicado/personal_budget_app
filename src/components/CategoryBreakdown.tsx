import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
}

export function CategoryBreakdown({ categoryTotals }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Filter for expenses (negative values) and use absolute amounts
  const expenses = Object.entries(categoryTotals)
    .filter(([, amount]) => amount < 0)
    .map(([category, amount]) => [category, Math.abs(amount)] as [string, number])

  if (expenses.length === 0) return null

  // Sort by absolute amount descending
  const sortedCategories = expenses
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10) // Top 10 categories

  const totalSpending = expenses.reduce((sum, [, amount]) => sum + amount, 0)
  const maxAmount = Math.max(...expenses.map(([, amount]) => amount))

  return (
    <div className="category-breakdown">
      <h3>Top Spending Categories</h3>
      <ul className="breakdown-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = (amount / totalSpending) * 100
          const formattedAmount = `$${amount.toFixed(2)}`
          return (
            <li key={category} className="breakdown-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className="category-amount">{formattedAmount}</span>
              </div>
              <div className="category-bar-container">
                <div
                  className="category-bar"
                  role="meter"
                  aria-valuenow={amount}
                  aria-valuemin={0}
                  aria-valuemax={maxAmount}
                  aria-valuetext={formattedAmount}
                  aria-label={`${category} spending`}
                  style={{
                    width: `${(amount / maxAmount) * 100}%`,
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
          <span className="total-amount">${totalSpending.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {expenses.length} categories
        </div>
      </div>
    </div>
  )
}
