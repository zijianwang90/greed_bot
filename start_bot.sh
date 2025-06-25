#!/bin/bash

# Fear & Greed Index Bot Startup Script
# This script ensures the virtual environment is activated before starting the bot

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🤖 Starting Fear & Greed Index Bot...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📁 Working directory: $SCRIPT_DIR${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}💡 Please run './install.sh' first${NC}"
    exit 1
fi

# Check if activate script exists
if [ ! -f "venv/bin/activate" ]; then
    echo -e "${RED}❌ Virtual environment is incomplete!${NC}"
    echo -e "${YELLOW}💡 Please delete 'venv' folder and run './install.sh' again${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo -e "${GREEN}✅ Virtual environment activated: $VIRTUAL_ENV${NC}"
else
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo -e "${RED}❌ Configuration file not found!${NC}"
    echo -e "${YELLOW}💡 Please copy config.example.py to config.py and configure it${NC}"
    exit 1
fi

# Check if main dependencies are installed
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
python -c "import telegram" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ python-telegram-bot not installed!${NC}"
    echo -e "${YELLOW}💡 Running: pip install -r requirements-minimal.txt${NC}"
    pip install -r requirements-minimal.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ All checks passed!${NC}"

# Start the bot
echo -e "${GREEN}🚀 Starting bot...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the bot${NC}"
echo ""

python main.py 