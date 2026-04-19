import { render, screen } from '@testing-library/react'
import { SummaryStats } from '../SummaryStats'
import { describe, it, expect } from 'vitest'

describe('SummaryStats', () => {
  const mockStats = {
    total_inflow: 5000,
    total_outflow: 3000,
    net_total: 2000,
    avg_monthly_inflow: 5100, // Changed to be unique
    avg_monthly_outflow: 3100, // Changed to be unique
    transaction_count: 50,
    unique_categories: 10,
    date_range: {
      start: '2024-01-01',
      end: '2024-01-31'
    }
  }

  it('renders summary statistics correctly', () => {
    render(<SummaryStats stats={mockStats} />)

    expect(screen.getByText('Summary Statistics')).toBeInTheDocument()
    expect(screen.getByText('$5000.00')).toBeInTheDocument()
    expect(screen.getByText('$3000.00')).toBeInTheDocument()
    expect(screen.getByText('$2000.00')).toBeInTheDocument()
    expect(screen.getByText('$5100.00')).toBeInTheDocument()
    expect(screen.getByText('$3100.00')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('2024-01-01 to 2024-01-31')).toBeInTheDocument()
  })

  it('applies correct class for positive net total', () => {
    const { container } = render(<SummaryStats stats={mockStats} />)
    const netCard = container.querySelector('.stat-card.net')
    expect(netCard).toHaveClass('positive')
  })

  it('applies correct class for negative net total', () => {
    const negativeStats = { ...mockStats, net_total: -500 }
    const { container } = render(<SummaryStats stats={negativeStats} />)
    const netCard = container.querySelector('.stat-card.net')
    expect(netCard).toHaveClass('negative')
  })
})
