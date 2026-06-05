import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'

describe('CategoryBreakdown', () => {
  const mockTotals = {
    'Food': 500,
    'Rent': 1200,
    'Utilities': 150.25,
    'Income': -3000 // Test that magnitudes are used even if negative
  }

  it('renders top categories correctly sorted by magnitude', () => {
    const { container } = render(<CategoryBreakdown categoryTotals={mockTotals} />)

    expect(screen.getByText('Income')).toBeInTheDocument() // -3000 magnitude is highest
    expect(screen.getByText('$3000.00')).toBeInTheDocument()
    expect(screen.getByText('Rent')).toBeInTheDocument()
    expect(screen.getByText('$1200.00')).toBeInTheDocument()

    // Check that Income is first (magnitude 3000 > 1200)
    const categoryNames = container.querySelectorAll('.category-name')
    expect(categoryNames[0].textContent).toBe('Income')
    expect(categoryNames[1].textContent).toBe('Rent')
  })

  it('limits to top 10 categories', () => {
    const largeMockTotals: Record<string, number> = {}
    for (let i = 1; i <= 15; i++) {
      largeMockTotals[`Category ${i}`] = i * 10
    }

    render(<CategoryBreakdown categoryTotals={largeMockTotals} />)

    const items = screen.getAllByRole('listitem')
    expect(items).toHaveLength(10)
    // Highest should be Category 15
    expect(screen.getByText('Category 15')).toBeInTheDocument()
  })

  it('handles empty data', () => {
    render(<CategoryBreakdown categoryTotals={{}} />)
    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })

  it('renders a custom title and level', () => {
    render(
      <CategoryBreakdown
        categoryTotals={mockTotals}
        title="Custom Report"
        titleLevel="h2"
      />
    )

    const title = screen.getByText('Custom Report')
    expect(title.tagName).toBe('H2')
  })
})
