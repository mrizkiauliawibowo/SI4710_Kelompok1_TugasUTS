#!/bin/bash
echo "🍕 Food Delivery System - Setup"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x scripts/*.sh
mkdir -p logs
echo "✅ Setup completed! Run: ./scripts/run-all.sh"