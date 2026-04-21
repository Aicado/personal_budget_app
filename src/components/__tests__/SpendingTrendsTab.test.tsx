import { render, screen, waitFor } from '@testing-library/react'
import { SpendingTrendsTab } from '../tabs/SpendingTrendsTab'
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock fetch
global.fetch = vi.fn()

describe('SpendingTrendsTab', () => {
  const mockData = {
    monthly_trends: {
      months: ['2024-01'],
      inflows: [5000],
      outflows: [3000],
      net_amounts: [2000]
    }
  }

  beforeEach(() => {
    vi.resetAllMocks()
  })

  it('renders data after loading', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockData
    })

    render(<SpendingTrendsTab />)

    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument()
    }, { timeout: 2000 })

    // Use getAllByText because it appears in both chart and table
    expect(screen.getAllByText('2024-01').length).toBeGreaterThan(0)
    expect(screen.getAllByText('$5000.00').length).toBeGreaterThan(0)
  })

  it('renders error message on fetch failure', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: false
    })

    render(<SpendingTrendsTab />)

    await waitFor(() => {
      expect(screen.getByText(/Failed to fetch/i)).toBeInTheDocument()
    })
  })
})
