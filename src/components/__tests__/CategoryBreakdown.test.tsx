import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown', () => {
  const mockTotals = {
    'Food': 500.00,
    'Rent': 1500.00,
    'Utilities': 200.00
  }

  it('renders category totals correctly with absolute value scaling and custom title', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} title="Custom Title" />)

    expect(screen.getByText('Custom Title')).toBeInTheDocument()
    expect(screen.getByText('Food')).toBeInTheDocument()
    expect(screen.getByText('$500.00')).toBeInTheDocument()
    expect(screen.getByText('Rent')).toBeInTheDocument()
    expect(screen.getByText('$1500.00')).toBeInTheDocument()
    expect(screen.getByText('Total Volume:')).toBeInTheDocument()
    expect(screen.getByText('$2200.00')).toBeInTheDocument()
  })

  it('handles negative values correctly (mixed income/expense)', () => {
    const mixedTotals = {
      'Salary': 5000.00,
      'Rent': -1500.00,
      'Groceries': -500.00
    }
    render(<CategoryBreakdown categoryTotals={mixedTotals} />)

    // Should sort by absolute value descending: Salary (5000), Rent (1500), Groceries (500)
    const rows = screen.getAllByRole('listitem')
    expect(rows).toHaveLength(3)
    expect(rows[0]).toHaveTextContent('Salary')
    expect(rows[1]).toHaveTextContent('Rent')
    expect(rows[2]).toHaveTextContent('Groceries')

    // Total Volume should be sum of absolute values
    expect(screen.getByText('$7000.00')).toBeInTheDocument()

    // Check ARIA labels for income/expense distinction
    expect(screen.getByLabelText('Salary income: $5000.00 (71%)')).toBeInTheDocument()
    expect(screen.getByLabelText('Rent expense: $1500.00 (21%)')).toBeInTheDocument()
  })

  it('returns null when no categories provided', () => {
    const { container } = render(<CategoryBreakdown categoryTotals={{}} />)
    expect(container.firstChild).toBeNull()
  })
})
