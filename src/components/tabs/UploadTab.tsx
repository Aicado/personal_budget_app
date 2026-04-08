import React, { useState } from 'react'
import { FileUpload } from '../FileUpload'
import { SummaryStats } from '../SummaryStats'
import { MonthlySummary } from '../MonthlySummary'
import { CategoryBreakdown } from '../CategoryBreakdown'
import '../FileUpload.css'
import './Tabs.css'

interface AnalysisResult {
  filename: string
  monthly_trends: {
    months: string[]
    net_amounts: number[]
    outflows: number[]
    inflows: number[]
  }
  category_trends: {
    months: string[]
    categories: string[]
    data: Record<string, number[]>
  }
  category_totals: Record<string, number>
  summary_stats: {
    total_inflow: number
    total_outflow: number
    net_total: number
    avg_monthly_inflow: number
    avg_monthly_outflow: number
    transaction_count: number
    unique_categories: number
    date_range: {
      start: string
      end: string
    }
  }
  database_report?: {
    filename: string
    transactions_in_file: number
    transactions_added: number
    duplicates_found: number
  }
}

interface UploadTabProps {
  onAnalysisComplete: (data: AnalysisResult | null) => void
}

export const UploadTab: React.FC<UploadTabProps> = ({ onAnalysisComplete }) => {
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)
  const [showCategoryModal, setShowCategoryModal] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState<string>('all')
  const [categories, setCategories] = useState<string[]>([])

  const handleAnalysisComplete = (data: AnalysisResult) => {
    setAnalysisData(data)
    // Extract categories from the data
    const cats = Object.keys(data.category_totals)
    setCategories(cats)
    // Show verification modal
    setShowCategoryModal(true)
    onAnalysisComplete(data)
  }

  const handleConfirmCategories = () => {
    setShowCategoryModal(false)
  }

  return (
    <div className="upload-tab">
      <FileUpload onAnalysisComplete={handleAnalysisComplete} />

      {analysisData && (
        <div className="results-section">
          <div className="upload-report">
            <h3>📋 Upload Report</h3>
            <div className="report-info">
              <p><strong>File:</strong> {analysisData.filename}</p>
              {analysisData.database_report && (
                <>
                  <p><strong>Transactions in file:</strong> {analysisData.database_report.transactions_in_file}</p>
                  <p><strong>Transactions added:</strong> <span className="highlight-added">{analysisData.database_report.transactions_added}</span></p>
                  <p><strong>Duplicates found:</strong> {analysisData.database_report.duplicates_found}</p>
                </>
              )}
            </div>
          </div>

          <SummaryStats stats={analysisData.summary_stats} />
          <MonthlySummary
            months={analysisData.monthly_trends.months}
            inflows={analysisData.monthly_trends.inflows}
            outflows={analysisData.monthly_trends.outflows}
            netAmounts={analysisData.monthly_trends.net_amounts}
          />
          <CategoryBreakdown categoryTotals={analysisData.category_totals} />
        </div>
      )}

      {showCategoryModal && (
        <div className="modal-overlay" onClick={() => setShowCategoryModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Verify Categories & Select Account</h2>
              <button className="modal-close" onClick={() => setShowCategoryModal(false)}>✕</button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="account-select">Select Account to Add Transactions To:</label>
                <select 
                  id="account-select"
                  value={selectedAccount}
                  onChange={(e) => setSelectedAccount(e.target.value)}
                  className="form-control"
                >
                  <option value="all">All Accounts</option>
                  <option value="discover">Discover Checking</option>
                  <option value="capital-one">Capital One Venture X</option>
                  <option value="schwab">Schwab Checking</option>
                  <option value="citi">Citi Custom</option>
                </select>
              </div>

              <div className="form-group">
                <label>Categories Detected in File:</label>
                <div className="categories-list">
                  {categories.map((category, idx) => (
                    <div key={idx} className="category-item">
                      <input type="checkbox" defaultChecked id={`cat-${idx}`} />
                      <label htmlFor={`cat-${idx}`}>{category}</label>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCategoryModal(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={handleConfirmCategories}>
                Confirm & Add Transactions
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
