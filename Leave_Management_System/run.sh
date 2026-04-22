#!/bin/bash
# Quick Start Guide for Leave Management System

echo "🚀 Leave Management System - Quick Start"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python is installed"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run setup script
echo "🔧 Setting up demo data..."
python setup.py
echo "✅ Demo data created"
echo ""

# Run application
echo "🌐 Starting the Leave Management System..."
echo "📍 Open your browser and go to: http://localhost:5000"
echo ""
echo "Demo Credentials:"
echo "  Admin: username=admin, password=admin123"
echo "  Employee: username=employee, password=emp123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
