import { useMemo } from 'react'
import './CategoryBreakdown.css'

interface CategoryBreakdownProps {
  categoryTotals: Record<string, number>
  title?: string
}

export function CategoryBreakdown({ categoryTotals, title = "Top Spending Categories" }: CategoryBreakdownProps) {
  const { sortedCategories, totalAbs, maxAmount } = useMemo(() => {
    if (!categoryTotals) return { sortedCategories: [], totalAbs: 0, maxAmount: 0 }

    const entries = Object.entries(categoryTotals)

    // Sort by absolute value descending to highlight most significant activity
    const sorted = [...entries]
      .sort(([, a], [, b]) => Math.abs(b) - Math.abs(a))
      .slice(0, 10)

    const total = entries.reduce((sum, [, val]) => sum + Math.abs(val), 0)
    const max = entries.length > 0 ? Math.max(...entries.map(([, val]) => Math.abs(val))) : 0

    return { sortedCategories: sorted, totalAbs: total, maxAmount: max }
  }, [categoryTotals])

  if (sortedCategories.length === 0) return null

  return (
    <div className="category-breakdown">
      <h3>{title}</h3>
      <ul className="categories-list">
        {sortedCategories.map(([category, amount]) => {
          const absAmount = Math.abs(amount)
          const percentage = totalAbs > 0 ? (absAmount / totalAbs) * 100 : 0
          const isIncome = amount > 0

          return (
            <li key={category} className="category-item">
              <div className="category-header">
                <span className="category-name">{category}</span>
                <span className={`category-amount ${isIncome ? 'value-positive' : 'value-negative'}`}>
                  ${absAmount.toFixed(2)}
                </span>
              </div>
              <div className="category-bar-container">
                <div
                  className={`category-bar ${isIncome ? 'income' : 'expense'}`}
                  role="meter"
                  aria-valuenow={absAmount}
                  aria-valuemin={0}
                  aria-valuemax={maxAmount}
                  aria-label={`${category} ${isIncome ? 'income' : 'expense'}: $${absAmount.toFixed(2)} (${Math.round(percentage)}%)`}
                  style={{
                    width: maxAmount > 0 ? `${(absAmount / maxAmount) * 100}%` : '0%',
                  }}
                />
              </div>
              <div className="category-percentage">{percentage.toFixed(1)}% of total volume</div>
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
