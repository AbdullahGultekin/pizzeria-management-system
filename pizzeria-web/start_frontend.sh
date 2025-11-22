#!/bin/bash

# Frontend Start Script
cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start frontend
echo "Starting frontend on http://localhost:5173"
npm run dev
