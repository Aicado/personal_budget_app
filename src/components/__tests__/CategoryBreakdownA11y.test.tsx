import { render, screen, within } from '@testing-library/react'
import { CategoryBreakdown } from '../CategoryBreakdown'
import { describe, it, expect } from 'vitest'

describe('CategoryBreakdown Accessibility', () => {
  const mockTotals = {
    'Food': 500.00,
    'Rent': 1500.00,
  }

  it('has correct ARIA attributes for progress bars', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)

    const foodBar = screen.getByLabelText(/Food spending: \$500.00/)
    expect(foodBar).toBeInTheDocument()
    expect(foodBar).toHaveAttribute('role', 'meter')
    expect(foodBar).toHaveAttribute('aria-valuenow', '500')
    expect(foodBar).toHaveAttribute('aria-valuemin', '0')
    expect(foodBar).toHaveAttribute('aria-valuemax', '1500')

    const rentBar = screen.getByLabelText(/Rent spending: \$1500.00/)
    expect(rentBar).toBeInTheDocument()
    expect(rentBar).toHaveAttribute('role', 'meter')
    expect(rentBar).toHaveAttribute('aria-valuenow', '1500')
    expect(rentBar).toHaveAttribute('aria-valuemin', '0')
    expect(rentBar).toHaveAttribute('aria-valuemax', '1500')
  })

  it('uses semantic list for categories', () => {
    render(<CategoryBreakdown categoryTotals={mockTotals} />)

    const list = screen.getByRole('list')
    expect(list).toHaveClass('categories-list')

    const items = within(list).getAllByRole('listitem')
    expect(items).toHaveLength(2)
  })

  it('renders with custom title and heading level', () => {
    render(
      <CategoryBreakdown
        categoryTotals={mockTotals}
        title="Spending Stats"
        titleLevel="h2"
      />
    )

    const heading = screen.getByRole('heading', { level: 2 })
    expect(heading).toHaveTextContent('Spending Stats')
  })
})
