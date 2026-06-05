import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
  titleLevel?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
}

export function CategoryBreakdown({
  categoryTotals,
  title = 'Top Spending Categories',
  titleLevel = 'h3'
}: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Use absolute values for visualization and sorting.
  // We don't filter for < 0 here to be robust to different data conventions,
  // but we treat all magnitudes as "spending" for this breakdown.
  const processedData = Object.entries(categoryTotals)
    .map(([category, amount]) => [category, Math.abs(amount)] as [string, number])
    .filter(([, amount]) => amount > 0)

  if (processedData.length === 0) {
    return (
      <div className="category-breakdown no-expenses">
        <p>No spending data available for the selected period.</p>
      </div>
    )
  }

  // Sort by amount descending (highest magnitude first)
  const sortedCategories = processedData
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10) // Top 10 categories

  const totalMagnitude = processedData.reduce((sum, [, amount]) => sum + amount, 0)
  const maxAmount = Math.max(...processedData.map(([, amount]) => amount))

  const TitleTag = titleLevel

  return (
    <div className="category-breakdown">
      <TitleTag className="category-breakdown-title">{title}</TitleTag>
      <ul className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = totalMagnitude > 0 ? (amount / totalMagnitude) * 100 : 0
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
                  aria-label={`${category}: $${amount.toFixed(2)} (${percentage.toFixed(1)}% of total)`}
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
          <span>Total:</span>
          <span className="total-amount">${totalMagnitude.toFixed(2)}</span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {processedData.length} categories
        </div>
      </div>
    </div>
  )
}
