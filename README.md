# Personal Budget App

A full-stack application to analyze personal budget data and visualize monthly spending trends, similar to YNAB's built-in reports.

## 🎯 Features

- **File Upload**: Upload YNAB transaction export CSV files
- **Monthly Trends**: Visualize income, expenses, and net monthly trends
- **Category Breakdown**: See top spending categories with percentage breakdowns
- **Summary Statistics**: Get comprehensive stats about your finances
- **Multi-file Support**: Analyze multiple transaction files at once
- **Responsive Design**: Works on desktop and mobile devices

## 🛠 Tech Stack

### Frontend
- **React 19** with TypeScript
- **Vite** for fast development and building
- **CSS3** for styling with responsive design

### Backend
- **Python 3.10**
- **FastAPI** for REST API
- **Pandas** for data analysis
- **uv** for dependency management and virtual environments

## 📋 Prerequisites

- Node.js 16+ (for frontend)
- Python 3.10+ (for backend)
- `uv` Python package manager ([install uv](https://docs.astral.sh/uv/))

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Node dependencies
npm install

# Create / refresh the Python virtual environment and install dependencies
uv venv --clear .venv
uv sync
```

### 2. Run the Application

#### Option A: Run both frontend and backend together
```bash
bash start.sh
```

#### Option B: Run separately (recommended for development)

Terminal 1 - Backend:
```bash
# Run backend with uv in development mode
uv run -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
npm run dev
```

#### Option C: Run a Python script directly with uv
```bash
uv run python src/backend/your_script.py
```

### 3. Open in Browser
Navigate to `http://localhost:5173`

## 📁 Project Structure

```
ynab-analyzer/
├── src/
│   ├── backend/                    # Python FastAPI backend
│   │   ├── main.py                # FastAPI application
│   │   ├── transaction_analyzer.py # Core analysis logic
│   │   └── __init__.py
│   ├── components/                # React components
│   │   ├── FileUpload.tsx
│   │   ├── MonthlySummary.tsx
│   │   ├── CategoryBreakdown.tsx
│   │   ├── SummaryStats.tsx
│   │   └── *.css                  # Component styles
│   ├── App.tsx                    # Main React component
│   ├── main.tsx                   # React entry point
│   ├── App.css
│   └── index.css
├── ynab_data/                     # Sample YNAB export files
├── pyproject.toml                 # Python project configuration
├── package.json                   # Node.js project configuration
├── vite.config.ts                 # Vite configuration
├── tsconfig.json                  # TypeScript configuration
├── setup.sh                        # Setup script
├── start.sh                        # Start script
└── README.md                       # This file
```

## 📊 How to Use

1. **Export from YNAB**: Export your transaction data from YNAB as CSV files
2. **Upload Files**: Click the upload area and select one or multiple CSV files
3. **View Analysis**: The app will automatically analyze and display:
   - Summary statistics (total income, expenses, net)
   - Monthly trends with interactive visualizations
   - Top spending categories
   - Date range and transaction count

## 🔧 Environment Management with uv

### Virtual Environment
```bash
# Create/recreate virtual environment
uv venv --clear .venv

# Activate the environment (if using directly)
source .venv/bin/activate
```

### Dependency Management
```bash
# Sync dependencies from pyproject.toml
uv sync

# Add a new dependency
uv add <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv lock --upgrade
```

### Running Commands
```bash
# Run with the managed environment
uv run <command>

# Run Python scripts
uv run python script.py

# Run the backend server
uv run -m uvicorn src.backend.main:app --reload
```

## 🏗 Building for Production

### Frontend
```bash
npm run build
# Output: dist/
```

### Backend Deployment
```bash
# Build with uv
uv build

# Or use directly with:
uv run -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
```

## 📝 API Endpoints

### POST /analyze
Upload a single CSV file for analysis.

**Request:**
```bash
curl -X POST -F "file=@transactions.csv" http://localhost:8000/analyze
```

**Response:**
```json
{
  "filename": "transactions.csv",
  "monthly_trends": { ... },
  "category_trends": { ... },
  "category_totals": { ... },
  "summary_stats": { ... }
}
```

### POST /analyze-multiple
Upload multiple CSV files for combined analysis.

**Request:**
```bash
curl -X POST -F "files=@file1.csv" -F "files=@file2.csv" http://localhost:8000/analyze-multiple
```

### GET /health
Health check endpoint.

## 🎨 Customization

### Styling
All component styles are in individual `.css` files in `src/components/`. Modify colors and layouts as needed.

### Data Analysis
Modify `src/backend/transaction_analyzer.py` to add custom analysis features.

## 📦 Adding Dependencies

### Frontend (Node.js)
```bash
npm install <package-name>
```

### Backend (Python)
```bash
uv add <package-name>
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000
# Kill the process if needed
kill -9 <PID>
```

### Frontend won't connect to backend
- Make sure backend is running on `http://localhost:8000`
- Check CORS settings in `src/backend/main.py`
- Check browser console for error messages

### CSV parsing errors
- Ensure CSV format matches YNAB export format
- Check column names (should include: Date, Category, Outflow, Inflow)
- Verify CSV encoding is UTF-8

## 📚 CSV Format Requirements

Your YNAB export CSV should have these columns:
- `Date` - Transaction date (MM/DD/YYYY format)
- `Payee` - Transaction payee
- `Category` - Transaction category
- `Outflow` - Money spent
- `Inflow` - Money received

## 🔐 Security Notes

- Only process your own financial data
- This app runs locally by default
- Uploaded files are not stored permanently
- For production, implement proper authentication

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## 📞 Support

For issues or questions, please open a GitHub issue or contact the maintainer.

---

Happy budgeting! 💰📊
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
