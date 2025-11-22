#!/bin/bash

# Backend Start Script
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check if menu data needs to be imported
if [ ! -f "pizzeria.db" ] || [ ! -s "pizzeria.db" ]; then
    echo "Importing menu data..."
    python import_menu.py
fi

# Start backend
echo "Starting backend on http://localhost:8000"
python run.py
