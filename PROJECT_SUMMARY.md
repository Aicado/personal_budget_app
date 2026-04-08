# 🎉 YNAB Analyzer - Project Summary

## ✅ What Was Built

A complete full-stack application for analyzing YNAB transaction data with monthly trends visualization, similar to YNAB's built-in reports.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ • File Upload Component                                     │  │
│  │ • Monthly Summary with trends                               │  │
│  │ • Category Breakdown dashboard                              │  │
│  │ • Summary Statistics cards                                  │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────────────┘
                       │ REST API
┌──────────────────────┴───────────────────────────────────────────┐
│             FastAPI Backend (Port 8000)                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ • TransactionAnalyzer class (pandas-based analysis)         │  │
│  │ • /analyze endpoint (single file)                           │  │
│  │ • /analyze-multiple endpoint (batch processing)             │  │
│  │ • Monthly trends & category aggregation                     │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
ynab-analyzer/
├── 📂 src/
│   ├── 📂 backend/                  # Python FastAPI backend
│   │   ├── main.py                  # FastAPI app & endpoints
│   │   ├── transaction_analyzer.py  # Analysis engine
│   │   └── __init__.py
│   ├── 📂 components/               # React components
│   │   ├── FileUpload.tsx           # CSV upload handler
│   │   ├── MonthlySummary.tsx       # Monthly trends display
│   │   ├── CategoryBreakdown.tsx    # Spending by category
│   │   ├── SummaryStats.tsx         # Financial metrics
│   │   └── *.css                    # Component styling
│   ├── App.tsx                      # Main application
│   ├── main.tsx                     # React entry
│   ├── App.css
│   └── index.css
├── 📂 ynab_data/                    # Sample data files
├── 📂 .venv/                        # Python virtual environment
├── 📂 node_modules/                 # Node dependencies
├── pyproject.toml                   # Python project config (uv)
├── package.json                     # Node project config
├── vite.config.ts                   # Vite bundler config
├── tsconfig.json                    # TypeScript config
├── Makefile                         # Build commands
├── Dockerfile                       # Docker container
├── docker-compose.yml               # Docker orchestration
├── setup.sh                         # Setup script
├── start.sh                         # Start script
├── README.md                        # Full documentation
├── QUICKSTART.md                    # 5-minute setup guide
├── DEPLOYMENT.md                    # Production deployment
├── UV_GUIDE.md                      # UV package manager guide
└── uv.lock                          # Python lock file
```

## 🛠 Technology Stack

### Frontend
- **React 19** - UI framework with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool
- **CSS3** - Responsive styling

### Backend
- **Python 3.10** - Runtime
- **FastAPI** - Modern web framework
- **Pandas** - Data analysis & manipulation
- **Uvicorn** - ASGI server

### Development & Deployment
- **uv** - Python package & environment management
- **Docker** - Containerization
- **Make** - Build automation
- **npm** - Node package management

## 🚀 Key Features

### 1. File Upload
- Single and batch file upload
- CSV format validation
- Real-time processing

### 2. Data Analysis
- Monthly income/expense trends
- Category-based spending breakdown
- Comprehensive financial statistics
- Date range analysis
- Transaction counting

### 3. Visualization
- Monthly summary cards with bar charts
- Category breakdown with percentages
- Summary statistics dashboard
- Responsive grid layout

### 4. API Endpoints
- `POST /analyze` - Single file analysis
- `POST /analyze-multiple` - Batch analysis
- `GET /health` - Health check

## 📊 Analysis Capabilities

The `TransactionAnalyzer` class provides:

```python
# Monthly trends
get_monthly_trends()  # Income, expenses, net by month

# Category analysis
get_category_trends()  # Spending by category over time
get_category_totals()  # Total per category

# Statistics
get_summary_stats()   # Comprehensive financial metrics
```

## 📝 How to Get Started

### Quick Start (5 minutes)
```bash
make setup              # Install dependencies
make dev               # Run frontend + backend
# Open http://localhost:5173
```

### Separate Development
```bash
make dev-backend       # Terminal 1 - Python server
make dev-frontend      # Terminal 2 - React dev server
```

### Using UV Directly
```bash
uv sync               # Install Python deps
uv run -m uvicorn src.backend.main:app --reload
npm run dev           # Frontend in another terminal
```

## 🔧 Commands Reference

```bash
# Setup & Installation
make setup          # Full setup
make install        # Install deps only

# Development
make dev            # Run both servers
make dev-backend    # Backend only
make dev-frontend   # Frontend only

# Building
make build          # Build for production
make build-backend  # Build Python wheel

# Maintenance
make lint           # Check code quality
make format         # Auto-format code
make clean          # Clean build artifacts
make help           # Show all commands
```

## 📦 UV Package Management

This project uses `uv` for Python management:

```bash
uv venv              # Create virtual environment
uv sync              # Install dependencies
uv add <package>     # Add dependency
uv run <command>     # Run command in venv
uv build             # Build package
```

**Benefits of uv:**
- ⚡ 10-100x faster than pip
- 🔒 Lock file for reproducible builds
- 📦 All-in-one Python tool
- 🎯 Zero-config setup

See [UV_GUIDE.md](UV_GUIDE.md) for detailed instructions.

## 🐳 Docker Deployment

```bash
# Build
docker build -t ynab-analyzer .

# Run
docker run -p 8000:8000 ynab-analyzer

# Or with Docker Compose
docker-compose up
```

## 🌐 Production Deployment

Multiple options supported:

- **Heroku** - Git push deployment
- **AWS** - EC2, Lambda, S3 + CloudFront
- **Google Cloud** - Cloud Run
- **DigitalOcean** - App Platform
- **Self-hosted** - Any server with Python & Node

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📋 CSV Format Requirements

Expected YNAB export columns:
- `Date` - MM/DD/YYYY format
- `Payee` - Transaction source/destination
- `Category` - Expense/income category
- `Outflow` - Amount spent
- `Inflow` - Amount received

## ✨ Key Implementation Details

### Frontend Components
1. **FileUpload** - Drag-drop CSV upload
2. **MonthlySummary** - Interactive monthly cards
3. **CategoryBreakdown** - Top 10 categories visualization
4. **SummaryStats** - Key metrics dashboard

### Backend Features
1. **Flexible CSV parsing** - Handles various formats
2. **Automatic date detection** - MM/DD/YYYY parsing
3. **Category aggregation** - Groups by category & month
4. **Summary statistics** - 8 key metrics computed
5. **CORS enabled** - Frontend-backend communication

## 🔒 Security Features

✅ Local processing - no cloud uploads
✅ CORS configured - controlled access
✅ Input validation - CSV format checking
✅ Error handling - graceful failures
✅ No data persistence - files processed in memory

## 📚 Documentation Files

- **README.md** - Complete project documentation
- **QUICKSTART.md** - 5-minute setup guide
- **UV_GUIDE.md** - UV package manager guide
- **DEPLOYMENT.md** - Production deployment guide

## 🎯 Next Steps

1. **Customize styling** - Edit CSS files in `src/components/`
2. **Add features** - Extend `TransactionAnalyzer` class
3. **Deploy** - Follow DEPLOYMENT.md
4. **Enhance analysis** - Add charts, exports, forecasting
5. **Add database** - Store historical data (optional)

## 🧪 Testing the Setup

The backend was tested with real YNAB data:
```
✅ Loaded 3,165 transactions
✅ Date range: 2023-11-22 to 2026-01-14
✅ Total income: $1,299,140.07
✅ Total expenses: $959,654.65
✅ 20 unique categories
```

## 🎓 Learning Resources

- **React**: https://react.dev
- **TypeScript**: https://www.typescriptlang.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pandas**: https://pandas.pydata.org/
- **uv**: https://docs.astral.sh/uv/

## 🤝 Contributing

The project is structured for easy extension:

1. Add new components in `src/components/`
2. Extend analysis in `src/backend/transaction_analyzer.py`
3. Add new endpoints in `src/backend/main.py`
4. Style with CSS modules

## 📞 Support & Issues

Check files in this order:
1. **QUICKSTART.md** - Quick setup help
2. **README.md** - Detailed docs
3. **DEPLOYMENT.md** - Production help
4. **UV_GUIDE.md** - Package management
5. Browser console - Frontend errors
6. Backend logs - Server errors

## 🎉 You're All Set!

Your YNAB Analyzer is ready to use. Start with:

```bash
make setup
make dev
```

Then open http://localhost:5173 and upload your YNAB CSV files!

Happy analyzing! 📊💰
