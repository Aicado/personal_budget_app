import './MonthlySummary.css'

interface MonthlySummaryProps {
  months: string[]
  inflows: number[]
  outflows: number[]
  netAmounts: number[]
}

export function MonthlySummary({ months, inflows, outflows, netAmounts }: MonthlySummaryProps) {
  if (!months || months.length === 0) return null

  // Calculate max values for scaling bars
  const maxOutflow = Math.max(...outflows)
  const maxInflow = Math.max(...inflows)

  return (
    <div className="monthly-summary">
      <h2>Monthly Trends</h2>
      <div className="summary-container">
        {months.map((month, index) => (
          <div key={month} className="month-card">
            <div className="month-label">{month}</div>
            <div className="flows-visualization">
              <div className="flow-item income">
                <div className="flow-label">Income</div>
                <div className="flow-bar-container">
                  <div
                    className="flow-bar income-bar"
                    role="meter"
                    aria-valuenow={inflows[index]}
                    aria-valuemin={0}
                    aria-valuemax={maxInflow}
                    aria-label={`${month} income: $${inflows[index].toFixed(2)}`}
                    style={{
                      width: `${(inflows[index] / maxInflow) * 100}%`,
                      minWidth: inflows[index] > 0 ? '2px' : '0',
                    }}
                  />
                </div>
                <div className="flow-amount">${inflows[index].toFixed(2)}</div>
              </div>
              <div className="flow-item expense">
                <div className="flow-label">Expenses</div>
                <div className="flow-bar-container">
                  <div
                    className="flow-bar expense-bar"
                    role="meter"
                    aria-valuenow={outflows[index]}
                    aria-valuemin={0}
                    aria-valuemax={maxOutflow}
                    aria-label={`${month} expenses: $${outflows[index].toFixed(2)}`}
                    style={{
                      width: `${(outflows[index] / maxOutflow) * 100}%`,
                      minWidth: outflows[index] > 0 ? '2px' : '0',
                    }}
                  />
                </div>
                <div className="flow-amount">${outflows[index].toFixed(2)}</div>
              </div>
            </div>
            <div className={`net-amount ${netAmounts[index] >= 0 ? 'positive' : 'negative'}`}>
              Net: ${netAmounts[index].toFixed(2)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
