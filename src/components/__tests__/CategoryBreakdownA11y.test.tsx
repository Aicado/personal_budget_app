import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'

describe('CategoryBreakdown Accessibility', () => {
  const mockTotals = {
    'Food': 542.50,
    'Rent': 1200.00
  }

  it('has accessible meter roles and labels', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)

    const meters = screen.getAllByRole('meter')
    expect(meters).toHaveLength(2)

    // Total is 1742.50. Rent (1200) is ~68.9%
    const rentMeter = screen.getByLabelText(/Rent: \$1200.00 \(68.9% of total\)/)
    expect(rentMeter).toBeInTheDocument()
    expect(rentMeter).toHaveAttribute('aria-valuenow', '1200')
    expect(rentMeter).toHaveAttribute('aria-valuemax', '1200') // Rent is max in this set
  })

  it('uses semantic list tags', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)

    expect(screen.getByRole('list')).toBeInTheDocument()
    expect(screen.getAllByRole('listitem')).toHaveLength(2)

    const list = screen.getByRole('list')
    expect(list.tagName).toBe('UL')
  })

  it('provides feedback when no data exists', () => {
    render(<CategoryBreakdown categoryTotals={{ 'Nothing': 0 }} />)
    expect(screen.getByText(/No spending data available/i)).toBeInTheDocument()
  })
})
