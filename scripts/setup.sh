#!/bin/bash
echo " Food Delivery System - Setup"
echo "===================================="

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh
chmod +x microservices/*/run.sh

# Create logs directory
mkdir -p logs

echo ""
echo " Setup completed!"
echo ""
echo " Next steps:"
echo "   ./scripts/run-all.sh    - Start all services"
echo "   ./scripts/stop-all.sh   - Stop all services"
echo ""
echo " Access: http://localhost:5000"