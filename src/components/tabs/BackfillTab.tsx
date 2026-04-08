import React from 'react'
import { BackfillStatus } from '../BackfillStatus'
import './Tabs.css'

export const BackfillTab: React.FC = () => {
  return (
    <div className="backfill-tab">
      <div className="tab-header">
        <h2>📥 Backfill Database</h2>
        <p>Load all existing YNAB CSV files from the data directory into the database</p>
      </div>
      <BackfillStatus />
    </div>
  )
}
