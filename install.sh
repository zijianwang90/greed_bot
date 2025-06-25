#!/bin/bash

# Fear & Greed Index Bot Installation Script
# This script helps install dependencies and set up the bot

set -e

echo "🤖 Fear & Greed Index Bot Installation Script"
echo "=============================================="

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python version is >= 3.8
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist or is incomplete
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    if [ -d "venv" ]; then
        echo "⚠️ Virtual environment exists but is incomplete, removing..."
        rm -rf venv
    fi
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "💡 Try running: sudo apt-get install python3-venv"
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment activation file not found"
    echo "🔧 Please delete the venv folder and run the script again"
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Try to install dependencies
echo "📥 Installing dependencies..."

# First try full requirements
if pip install -r requirements.txt; then
    echo "✅ All dependencies installed successfully!"
else
    echo "⚠️ Full installation failed, trying minimal dependencies..."
    
    # If full installation fails, try minimal
    if pip install -r requirements-minimal.txt; then
        echo "✅ Minimal dependencies installed successfully!"
        echo "⚠️ Some optional features may not be available"
    else
        echo "❌ Minimal installation also failed"
        echo "🔧 Trying to install core dependencies manually..."
        
        # Manual installation of core dependencies
        pip install python-telegram-bot requests aiohttp sqlalchemy apscheduler pandas beautifulsoup4 python-dotenv
        
        echo "✅ Core dependencies installed"
        echo "⚠️ Some features may be limited"
    fi
fi

# Create config file if it doesn't exist
if [ ! -f "config.py" ]; then
    echo "⚙️ Creating configuration file..."
    cp config.example.py config.py
    echo "✅ Config file created from template"
    echo "📝 Please edit config.py with your bot token and settings"
else
    echo "✅ Configuration file already exists"
fi

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit config.py with your Telegram bot token"
echo "2. Run: python main.py"
echo ""
echo "For troubleshooting, see the README.md file" 