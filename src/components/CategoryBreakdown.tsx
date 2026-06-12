import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
  titleLevel?: 'h2' | 'h3' | 'h4'
}

export function CategoryBreakdown({
  categoryTotals,
  title = 'Top Spending Categories',
  titleLevel: TitleTag = 'h3',
}: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Focus on spending (negative values) and use absolute values for sorting/visualization
  const spendingData = Object.entries(categoryTotals)
    .filter(([, amount]) => amount < 0)
    .map(([category, amount]) => [category, Math.abs(amount)] as [string, number])

  if (spendingData.length === 0) return null

  // Sort by amount descending
  const sortedCategories = spendingData.sort(([, a], [, b]) => b - a).slice(0, 10) // Top 10 categories

  const totalSpending = spendingData.reduce((sum, [, amount]) => sum + amount, 0)
  const maxAmount = Math.max(...spendingData.map(([, amount]) => amount))

  return (
    <div className="category-breakdown">
      <TitleTag>{title}</TitleTag>
      <ul className="breakdown-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = (amount / totalSpending) * 100
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
                  aria-label={`${category} spending`}
                  aria-valuetext={`$${amount.toFixed(2)}`}
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
          Showing top {sortedCategories.length} of {spendingData.length} categories
        </div>
      </div>
    </div>
  )
}
