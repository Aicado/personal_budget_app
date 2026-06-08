import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown', () => {
  const mockTotals = {
    'Food': 500.00,
    'Rent': 1500.00,
    'Utilities': 200.00
  }

  it('renders category totals correctly', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)

    expect(screen.getByText('Top Spending Categories')).toBeInTheDocument()
    expect(screen.getByText('Food')).toBeInTheDocument()
    expect(screen.getByText('$500.00')).toBeInTheDocument()
    expect(screen.getByText('Rent')).toBeInTheDocument()
    expect(screen.getByText('$1500.00')).toBeInTheDocument()
    expect(screen.getByText('Total Spending:')).toBeInTheDocument()
    expect(screen.getByText('$2200.00')).toBeInTheDocument()
  })

  it('renders with custom title and title level', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} title="Custom Title" titleLevel="h2" />)
    const title = screen.getByText('Custom Title')
    expect(title).toBeInTheDocument()
    expect(title.tagName).toBe('H2')
  })

  it('uses semantic list elements', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)
    expect(screen.getByRole('list')).toHaveClass('breakdown-list')
    expect(screen.getAllByRole('listitem')).toHaveLength(3)
  })

  it('returns null when no categories provided', () => {
    const { container } = render(<CategoryBreakdown categoryTotals={{}} />)
    expect(container.firstChild).toBeNull()
  })
})
