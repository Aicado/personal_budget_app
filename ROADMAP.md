# 🗺 Personal Budget App - Roadmap & Vision

## 🌟 The Vision
To build a seamless, high-performance web and mobile experience that empowers users to master their finances with minimal effort. The app serves as a "Financial Command Center" that can be checked monthly (or daily) to instantly understand cash flow, savings rate, and net worth evolution.

## 🚀 Phase 1: Core Foundation (Current)
- [x] Vectorized transaction processing with Polars.
- [x] Analytical storage with DuckDB.
- [x] Multi-file CSV ingestion pipeline.
- [x] Basic Monthly Trends and Category Breakdowns.
- [x] Local-first, privacy-focused architecture.

## 📈 Phase 2: Enhanced Visualization & Snapshots (Upcoming)
Focus on providing "at-a-glance" financial health metrics.

### 📸 Financial Snapshots Page
A dedicated dashboard providing preset views to quickly compare performance across timeframes:
- **Last Year View**: Comparison of total income vs. expenses for the previous calendar year.
- **Last Month View**: Deep dive into the most recently completed month's spending vs. budget.
- **Year-to-Date (YTD) View**: Cumulative progress for the current year.
- **Custom Range**: User-defined start and end dates for specific project/trip tracking.

### 💰 Comprehensive Financial Tracking
- **Income & Expense Tracking**: Dynamic Sankey diagrams or flow charts to visualize where money comes from and exactly where it goes.
- **Savings Rate Calculation**: Automated tracking of income minus expenses, expressed as a percentage.
- **Investment Integration**: Tracking of brokerage account snapshots to visualize wealth growth beyond just cash.
- **Net Worth Evolution**: A historical line chart showing the total value of all assets minus liabilities over time.

## 📱 Phase 3: Mobile & Cloud Integration
- **Responsive Mobile Web**: Optimization for "on-the-go" checking of balances and spending.
- **PWA Support**: Progressive Web App for home-screen access without an app store.
- **Secure Cloud Sync (Optional)**: Optional encrypted sync for users who want to access data across multiple devices while maintaining privacy.
- **Automated Bank Feeds**: Integration with Plaid or similar services to reduce reliance on manual CSV exports.

## 🛠 Phase 4: Intelligence & Forecasting
- **Spending Alerts**: Notifications when a category exceeds the historical 3-month average.
- **Retirement Forecasting**: Simple "Monte Carlo" simulations based on current savings rates and investment performance.
- **Tax Preparation Exports**: Simplified reports for tax-deductible categories.

---
*The goal is clarity, speed, and privacy. Your data, your insights.*
