# YNAB Analyzer - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
# One-time setup
make setup
```

### Step 2: Run the App

**Option A - Simplest (Recommended)**
```bash
make dev
```

**Option B - Separate terminals**
```bash
# Terminal 1
make dev-backend

# Terminal 2 (new terminal)
make dev-frontend
```

### Step 3: Open in Browser
```
http://localhost:5173
```

## 🎯 First Use

1. **Prepare your data**: Export transactions from YNAB as CSV
2. **Upload files**: Click the upload area or drag-and-drop CSV files
3. **View results**: Instantly see:
   - 📊 Monthly spending trends
   - 💰 Total income and expenses
   - 🏷️ Top spending categories
   - 📈 Summary statistics

## 📝 Expected CSV Format

Your YNAB export needs these columns:
```csv
Account,Flag,Date,Payee,Category Group/Category,Category Group,Category,Memo,Outflow,Inflow,Cleared
Checking,,"01/15/2026","Walmart","Monthly Flexible: Groceries","Monthly Flexible","Groceries","",100.00,0.00,Cleared
```

## 🔧 Commands Quick Reference

```bash
# Development
make dev              # Run everything
make dev-backend      # Just the API
make dev-frontend     # Just React

# Building
make build            # Build for production
make build-backend    # Build Python package

# Maintenance
make lint             # Check code quality
make format           # Auto-format code
make clean            # Remove build files
make help             # Show all commands
```

## 🚨 Troubleshooting

### "Cannot connect to backend"
```bash
# Make sure backend is running
make dev-backend
```

### Port already in use
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### CSV upload fails
- Check file format matches YNAB export
- Ensure Date, Category, Outflow, Inflow columns exist
- Verify file is UTF-8 encoded

## 📚 Next Steps

- Check [README.md](./README.md) for full documentation
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
- Explore component code in `src/components/`
- Customize analysis in `src/backend/transaction_analyzer.py`

## 🎨 Customization

### Change colors
Edit `src/components/*.css` files

### Add new analysis
Edit `src/backend/transaction_analyzer.py`

### Modify layout
Edit `src/App.tsx` and `src/components/*`

## 🐛 Debug Mode

```bash
# Backend with debug output
DEBUG=1 make dev-backend

# Frontend with React DevTools
# Install React Developer Tools browser extension
```

## 💾 Data Privacy

- ✅ All data stays on your computer
- ✅ Files not uploaded to servers (local only)
- ✅ Perfect for personal financial data

## 📞 Need Help?

1. Check the [README.md](./README.md)
2. Look at error messages in browser console
3. Check server logs: `make dev-backend`

---

Enjoy analyzing your spending! 💰📊
