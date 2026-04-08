import { useState } from 'react'
import './BackfillStatus.css'

interface FileReport {
  filename: string
  status: 'inserted' | 'skipped' | 'error'
  transactions_count?: number
  transactions_added?: number
  reason?: string
  error?: string
  date_range?: {
    start: string
    end: string
  }
}

interface BackfillResponse {
  status: string
  message: string
  total_files_found: number
  files_processed: number
  files_skipped: number
  total_transactions_added: number
  file_reports: FileReport[]
  database_summary?: {
    total_transactions: number
    unique_files: number
    unique_categories: number
    date_range: {
      start: string
      end: string
    }
    totals: {
      inflow: number
      outflow: number
    }
  }
}

interface BackfillStatusProps {
  onBackfillComplete?: (data: BackfillResponse) => void
}

export function BackfillStatus({ onBackfillComplete }: BackfillStatusProps) {
  const [loading, setLoading] = useState(false)
  const [backfillData, setBackfillData] = useState<BackfillResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleBackfill = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/backfill', {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`Backfill failed: ${response.statusText}`)
      }

      const data = await response.json()
      setBackfillData(data)
      onBackfillComplete?.(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="backfill-section">
      <div className="backfill-button-container">
        <button
          className="backfill-button"
          onClick={handleBackfill}
          disabled={loading}
        >
          {loading ? '⏳ Processing...' : '📥 Backfill Database'}
        </button>
        <p className="backfill-description">
          Load all YNAB CSV files from the data directory into the database
        </p>
      </div>

      {error && (
        <div className="backfill-error">
          <p>❌ {error}</p>
        </div>
      )}

      {backfillData && (
        <div className="backfill-report">
          <div className="report-header">
            <h3>📊 Backfill Report</h3>
            <p className={`status-badge ${backfillData.status}`}>
              {backfillData.status.toUpperCase()}
            </p>
          </div>

          <div className="report-summary">
            <div className="summary-stat">
              <div className="stat-value">{backfillData.total_files_found}</div>
              <div className="stat-label">Files Found</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{backfillData.files_processed}</div>
              <div className="stat-label">Inserted</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{backfillData.files_skipped}</div>
              <div className="stat-label">Skipped</div>
            </div>
            <div className="summary-stat">
              <div className="stat-value">{backfillData.total_transactions_added}</div>
              <div className="stat-label">Transactions Added</div>
            </div>
          </div>

          <div className="file-details">
            <h4>File-by-File Details</h4>
            <div className="files-list">
              {backfillData.file_reports.map((report, index) => (
                <div key={index} className={`file-item status-${report.status}`}>
                  <div className="file-header">
                    <span className="file-name">{report.filename}</span>
                    <span className={`status-badge status-${report.status}`}>
                      {report.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="file-details-inner">
                    {report.transactions_count && (
                      <p>
                        📦 Transactions in file: <strong>{report.transactions_count}</strong>
                      </p>
                    )}
                    {report.transactions_added !== undefined && (
                      <p>
                        ✅ Transactions added:{' '}
                        <strong className="highlight-added">{report.transactions_added}</strong>
                      </p>
                    )}
                    {report.date_range && (
                      <p>
                        📅 Date range: <strong>{report.date_range.start}</strong> to{' '}
                        <strong>{report.date_range.end}</strong>
                      </p>
                    )}
                    {report.reason && (
                      <p className="reason">ℹ️ {report.reason}</p>
                    )}
                    {report.error && (
                      <p className="error-text">⚠️ {report.error}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {backfillData.database_summary && (
            <div className="database-summary">
              <h4>💾 Database Summary After Backfill</h4>
              <div className="summary-grid">
                <div className="summary-card">
                  <p className="card-label">Total Transactions</p>
                  <p className="card-value">
                    {backfillData.database_summary.total_transactions.toLocaleString()}
                  </p>
                </div>
                <div className="summary-card">
                  <p className="card-label">Unique Files</p>
                  <p className="card-value">
                    {backfillData.database_summary.unique_files}
                  </p>
                </div>
                <div className="summary-card">
                  <p className="card-label">Categories</p>
                  <p className="card-value">
                    {backfillData.database_summary.unique_categories}
                  </p>
                </div>
                <div className="summary-card">
                  <p className="card-label">Date Range</p>
                  <p className="card-value-small">
                    {backfillData.database_summary.date_range.start} to{' '}
                    {backfillData.database_summary.date_range.end}
                  </p>
                </div>
                <div className="summary-card">
                  <p className="card-label">Total Inflow</p>
                  <p className="card-value-green">
                    ${backfillData.database_summary.totals.inflow.toFixed(2)}
                  </p>
                </div>
                <div className="summary-card">
                  <p className="card-label">Total Outflow</p>
                  <p className="card-value-red">
                    ${backfillData.database_summary.totals.outflow.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
