import { render, screen } from '@testing-library/react'
import { MonthlySummary } from '../MonthlySummary'
import { describe, it, expect } from 'vitest'

describe('MonthlySummary Accessibility', () => {
  const mockProps = {
    months: ['2024-01', '2024-02'],
    inflows: [5000, 6000],
    outflows: [3000, 4000],
    netAmounts: [2000, 2000]
  }

  it('has correct ARIA attributes for income and expense bars', () => {
    render(<MonthlySummary {...mockProps} />)

    // Check 2024-01 income bar
    const incomeBar1 = screen.getByLabelText(/2024-01 income: \$5000.00/)
    expect(incomeBar1).toBeInTheDocument()
    expect(incomeBar1).toHaveAttribute('role', 'meter')
    expect(incomeBar1).toHaveAttribute('aria-valuenow', '5000')
    expect(incomeBar1).toHaveAttribute('aria-valuemin', '0')
    expect(incomeBar1).toHaveAttribute('aria-valuemax', '6000')

    // Check 2024-01 expense bar
    const expenseBar1 = screen.getByLabelText(/2024-01 expenses: \$3000.00/)
    expect(expenseBar1).toBeInTheDocument()
    expect(expenseBar1).toHaveAttribute('role', 'meter')
    expect(expenseBar1).toHaveAttribute('aria-valuenow', '3000')
    expect(expenseBar1).toHaveAttribute('aria-valuemin', '0')
    expect(expenseBar1).toHaveAttribute('aria-valuemax', '4000')

    // Check 2024-02 income bar
    const incomeBar2 = screen.getByLabelText(/2024-02 income: \$6000.00/)
    expect(incomeBar2).toBeInTheDocument()
    expect(incomeBar2).toHaveAttribute('aria-valuenow', '6000')
    expect(incomeBar2).toHaveAttribute('aria-valuemax', '6000')

    // Check 2024-02 expense bar
    const expenseBar2 = screen.getByLabelText(/2024-02 expenses: \$4000.00/)
    expect(expenseBar2).toBeInTheDocument()
    expect(expenseBar2).toHaveAttribute('aria-valuenow', '4000')
    expect(expenseBar2).toHaveAttribute('aria-valuemax', '4000')
  })
})
