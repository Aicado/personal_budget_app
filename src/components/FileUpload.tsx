import { useState } from 'react'
import './FileUpload.css'

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
}

interface FileUploadProps {
  onAnalysisComplete: (data: AnalysisResult) => void
}

export function FileUpload({ onAnalysisComplete }: FileUploadProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      
      if (files.length === 1) {
        formData.append('file', files[0])
        const response = await fetch('http://localhost:8000/analyze', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }
        
        const data = await response.json()
        onAnalysisComplete(data)
      } else {
        for (let i = 0; i < files.length; i++) {
          formData.append('files', files[i])
        }
        
        const response = await fetch('http://localhost:8000/analyze-multiple', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`)
        }
        
        const data = await response.json()
        onAnalysisComplete(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="file-upload">
      <div className="upload-area">
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-icon">📁</div>
          <div className="upload-text">
            {loading ? 'Processing...' : 'Click to upload CSV files'}
          </div>
          <input
            id="file-input"
            type="file"
            accept=".csv"
            multiple
            onChange={handleFileChange}
            disabled={loading}
            className="file-input"
          />
        </label>
      </div>
      {error && <div className="error-message">{error}</div>}
    </div>
  )
}
