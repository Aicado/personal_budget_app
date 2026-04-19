import { render, screen } from '@testing-library/react'
import { MonthlySummary } from '../MonthlySummary'
import { describe, it, expect } from 'vitest'

describe('MonthlySummary', () => {
  const mockProps = {
    months: ['2024-01', '2024-02'],
    inflows: [5000, 6000],
    outflows: [3000, 4000],
    netAmounts: [2000, 2000]
  }

  it('renders monthly trends correctly', () => {
    render(<MonthlySummary {...mockProps} />)

    expect(screen.getByText('Monthly Trends')).toBeInTheDocument()
    expect(screen.getByText('2024-01')).toBeInTheDocument()
    expect(screen.getByText('2024-02')).toBeInTheDocument()
    expect(screen.getByText('$5000.00')).toBeInTheDocument()
    expect(screen.getByText('$6000.00')).toBeInTheDocument()

    // Using a more robust text matching for elements with broken up text or specific formatting
    const netTexts = screen.getAllByText((content, element) => {
        return element?.tagName.toLowerCase() === 'div' && content.includes('Net: $2000.00');
    });
    expect(netTexts).toHaveLength(2)
  })

  it('returns null when no months provided', () => {
    const { container } = render(<MonthlySummary months={[]} inflows={[]} outflows={[]} netAmounts={[]} />)
    expect(container.firstChild).toBeNull()
  })
})
