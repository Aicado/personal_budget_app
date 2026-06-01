import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown', () => {
  const mockTotals = {
    'Food': -500.00,
    'Rent': -1500.00,
    'Utilities': -200.00,
    'Salary': 5000.00
  }

  it('renders category totals correctly for expenses', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} type="expense" />)

    expect(screen.getByText('Top Spending Categories')).toBeInTheDocument()
    expect(screen.getByText('Food')).toBeInTheDocument()
    expect(screen.getByText('$500.00')).toBeInTheDocument()
    expect(screen.getByText('Rent')).toBeInTheDocument()
    expect(screen.getByText('$1500.00')).toBeInTheDocument()
    expect(screen.queryByText('Salary')).not.toBeInTheDocument()
    expect(screen.getByText('Total Spending:')).toBeInTheDocument()
    expect(screen.getByText('$2200.00')).toBeInTheDocument()
  })

  it('renders category totals correctly for income', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} type="income" />)

    expect(screen.getByText('Top Income Categories')).toBeInTheDocument()
    expect(screen.getByText('Salary')).toBeInTheDocument()
    // Use getAllByText because it appears in the list and in the total
    expect(screen.getAllByText('$5000.00').length).toBeGreaterThanOrEqual(1)
    expect(screen.queryByText('Food')).not.toBeInTheDocument()
    expect(screen.getByText('Total Income:')).toBeInTheDocument()
  })

  it('returns null when no categories match type', () => {
    const { container } = render(<CategoryBreakdown categoryTotals={{ 'Salary': 5000 }} type="expense" />)
    expect(container.firstChild).toBeNull()
  })

  it('returns null when no categories provided', () => {
    const { container } = render(<CategoryBreakdown categoryTotals={{}} />)
    expect(container.firstChild).toBeNull()
  })
})
