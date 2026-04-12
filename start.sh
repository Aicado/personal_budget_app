#!/bin/bash

# Start both backend and frontend
echo "🚀 Starting Personal Budget App..."
echo ""
echo "Starting backend on http://localhost:8000"
echo "Starting frontend on http://localhost:5173"
echo ""

# Start backend in background
npm run dev:backend &
BACKEND_PID=$!

# Start frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
