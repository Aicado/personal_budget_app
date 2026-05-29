import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown Accessibility', () => {
  const mockTotals = {
    'Food': 500.00,
    'Rent': 1500.00,
  }

  it('has correct ARIA attributes for progress bars and identifies activity type', () => {
    // One income, one expense
    const mixedTotals = {
      'Salary': 2000.00,
      'Rent': -1500.00,
    }
    render(<CategoryBreakdown categoryTotals={mixedTotals} />)

    const salaryBar = screen.getByLabelText(/Salary income: \$2000.00/)
    expect(salaryBar).toBeInTheDocument()
    expect(salaryBar).toHaveAttribute('role', 'meter')
    expect(salaryBar).toHaveAttribute('aria-valuenow', '2000')
    expect(salaryBar).toHaveAttribute('aria-valuemin', '0')
    expect(salaryBar).toHaveAttribute('aria-valuemax', '2000')

    const rentBar = screen.getByLabelText(/Rent expense: \$1500.00/)
    expect(rentBar).toBeInTheDocument()
    expect(rentBar).toHaveAttribute('role', 'meter')
    expect(rentBar).toHaveAttribute('aria-valuenow', '1500')
    expect(rentBar).toHaveAttribute('aria-valuemin', '0')
    expect(rentBar).toHaveAttribute('aria-valuemax', '2000')
  })
})
