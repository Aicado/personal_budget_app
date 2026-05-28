import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
}

export function CategoryBreakdown({ categoryTotals }: CategoryBreakdownProps) {
  if (!categoryTotals || Object.keys(categoryTotals).length === 0) return null

  // Sort by absolute magnitude descending
  const sortedCategories = Object.entries(categoryTotals)
    .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
    .slice(0, 10) // Top 10 categories

  const totalNet = Object.values(categoryTotals).reduce((sum, val) => sum + val, 0)
  const totalAbs = Object.values(categoryTotals).reduce((sum, val) => sum + Math.abs(val), 0)
  const maxAbsAmount = Math.max(...Object.values(categoryTotals).map(Math.abs))

  return (
    <div className="category-breakdown">
      <h4>Top Categories</h4>
      <div className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const percentage = totalAbs > 0 ? (Math.abs(amount) / totalAbs) * 100 : 0
          const isIncome = amount >= 0
          return (
            <div key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>{" "}
                <span className={`category-amount ${isIncome ? 'value-positive' : 'value-negative'}`}>
                  {isIncome ? '' : '-'}${Math.abs(amount).toFixed(2)}
                </span>
              </div>
              <div className="category-bar-container">
                <div
                  className={`category-bar ${isIncome ? 'income' : 'expense'}`}
                  role="meter"
                  aria-valuenow={Math.abs(amount)}
                  aria-valuemin={0}
                  aria-valuemax={maxAbsAmount > 0 ? maxAbsAmount : 1}
                  aria-label={`${category} ${isIncome ? 'income' : 'expense'}: $${Math.abs(
                    amount
                  ).toFixed(2)}`}
                  style={{
                    width: `${maxAbsAmount > 0 ? (Math.abs(amount) / maxAbsAmount) * 100 : 0}%`,
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total volume</div>
            </div>
          )
        })}
      </div>
      <div className="category-footer">
        <div className="total-spending">
          <span>Net Total:</span>
          <span className={`total-amount ${totalNet >= 0 ? 'value-positive' : 'value-negative'}`}>
            ${totalNet.toFixed(2)}
          </span>
        </div>
        <div className="category-count">
          Showing top {sortedCategories.length} of {Object.keys(categoryTotals).length} categories
        </div>
      </div>
    </div>
  )
}
