import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown Accessibility', () => {
  const mockTotals = {
    'Food': 500.00,
    'Rent': 1500.00,
  }

  it('has correct ARIA attributes for meters', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} title="Top Spending Categories" />)

    const foodBar = screen.getByLabelText(/Food income: \$500.00 \(25.0%\)/)
    expect(foodBar).toBeInTheDocument()
    expect(foodBar).toHaveAttribute('role', 'meter')
    expect(foodBar).toHaveAttribute('aria-valuenow', '500')
    expect(foodBar).toHaveAttribute('aria-valuemin', '0')
    expect(foodBar).toHaveAttribute('aria-valuemax', '1500')

    const rentBar = screen.getByLabelText(/Rent income: \$1500.00 \(75.0%\)/)
    expect(rentBar).toBeInTheDocument()
    expect(rentBar).toHaveAttribute('role', 'meter')
    expect(rentBar).toHaveAttribute('aria-valuenow', '1500')
    expect(rentBar).toHaveAttribute('aria-valuemin', '0')
    expect(rentBar).toHaveAttribute('aria-valuemax', '1500')
  })
})
