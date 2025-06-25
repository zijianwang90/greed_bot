# 📦 Fear & Greed Index Bot - Installation Guide

This guide helps you install the Fear & Greed Index Bot and resolve common dependency issues.

## 🚀 Quick Start

### Automatic Installation (Recommended)

**Linux/macOS:**
```bash
git clone https://github.com/yourusername/greed_bot.git
cd greed_bot
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
git clone https://github.com/yourusername/greed_bot.git
cd greed_bot
install.bat
```

The installation script will:
- ✅ Check Python version compatibility
- 📦 Create virtual environment
- ⬆️ Upgrade pip and setuptools
- 📥 Install dependencies (with fallback options)
- ⚙️ Create configuration file

## 🔧 Manual Installation

If the automatic installation doesn't work, follow these steps:

### 1. Prerequisites

- **Python 3.8+** (Python 3.11 recommended)
- **pip** (latest version)
- **git**

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/greed_bot.git
cd greed_bot
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 4. Upgrade pip

```bash
pip install --upgrade pip setuptools wheel
```

### 5. Install Dependencies

Try these options in order:

**Option 1: Full Installation**
```bash
pip install -r requirements.txt
```

**Option 2: Minimal Installation (if Option 1 fails)**
```bash
pip install -r requirements-minimal.txt
```

**Option 3: Core Dependencies Only**
```bash
pip install python-telegram-bot requests aiohttp sqlalchemy apscheduler pandas beautifulsoup4 python-dotenv
```

## 🚨 Troubleshooting Common Issues

### Issue 1: Cryptography Installation Fails

**Error:** `ERROR: Could not find a version that satisfies the requirement cryptography==41.0.8`

**Solution:**
```bash
# Use flexible version range
pip install "cryptography>=40.0.0,<46.0.0"

# Or install without specific version
pip install cryptography
```

**Platform-specific fixes:**

**macOS:**
```bash
brew install openssl libffi
export LDFLAGS="-L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
pip install cryptography
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install cryptography
```

**Windows:**
```cmd
pip install --upgrade pip setuptools wheel
pip install --only-binary=all cryptography
```

### Issue 2: Python Version Incompatibility

**Error:** `Requires-Python >=3.7,<3.11`

**Solution:**
- Use Python 3.8-3.11 (Python 3.11 recommended)
- Check your Python version: `python --version`
- Install compatible Python version if needed

### Issue 3: Pandas/NumPy Installation Issues

**Error:** Various compilation errors with pandas or numpy

**Solution:**
```bash
# Install pre-compiled binaries
pip install --only-binary=all pandas numpy

# Or use conda instead of pip
conda install pandas numpy
```

### Issue 4: Network/Proxy Issues

**Error:** Connection timeouts or SSL errors

**Solution:**
```bash
# Use trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements-minimal.txt

# Or configure proxy
pip install --proxy http://user:password@proxy.server:port -r requirements-minimal.txt
```

## 🧪 Verify Installation

Run the test script to verify everything is working:

```bash
python test_basic.py
```

Expected output:
```
🧪 Starting basic functionality tests...
==================================================

🔍 Running Import Test...
✅ All core dependencies imported successfully
✅ Import Test PASSED

🔍 Running Data Fetcher Test...
✅ DataFetcher initialized successfully
✅ Data Fetcher Test PASSED

... (more tests)

==================================================
🎯 Test Results: 5/5 tests passed
🎉 All tests passed! The bot should work correctly.
```

## ⚙️ Configuration

1. **Copy configuration template:**
   ```bash
   cp config.example.py config.py
   ```

2. **Edit config.py with your settings:**
   ```python
   TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   DATABASE_URL = "sqlite:///bot.db"
   DEFAULT_NOTIFICATION_TIME = "09:00"
   ```

3. **Get Telegram Bot Token:**
   - Message @BotFather on Telegram
   - Create new bot with `/newbot`
   - Copy the token to `config.py`

## 🚀 Run the Bot

```bash
python main.py
```

You should see:
```
INFO - Fear & Greed Index Bot starting...
INFO - Bot started successfully! Username: @your_bot_name
INFO - Notification scheduler started successfully
```

## 📋 Dependency Information

### Core Dependencies (requirements-minimal.txt)
- `python-telegram-bot` - Telegram Bot API
- `requests` - HTTP requests
- `aiohttp` - Async HTTP client
- `SQLAlchemy` - Database ORM
- `APScheduler` - Task scheduling
- `pandas` - Data processing
- `beautifulsoup4` - Web scraping
- `python-dotenv` - Environment variables

### Full Dependencies (requirements.txt)
Includes additional features:
- `cryptography` - Security (flexible version)
- `psycopg2-binary` - PostgreSQL support
- `yfinance` - Financial data
- `structlog` - Enhanced logging
- `pydantic` - Data validation

## 🐳 Alternative: Docker Installation

If you continue having issues, try Docker:

```bash
# Build Docker image
docker build -t greed-bot .

# Run with environment file
docker run -d --env-file .env greed-bot
```

## 🆘 Getting Help

If you're still having issues:

1. **Check Python version:** `python --version` (must be 3.8+)
2. **Check pip version:** `pip --version` (upgrade if old)
3. **Try minimal installation:** `pip install -r requirements-minimal.txt`
4. **Run tests:** `python test_basic.py`
5. **Check logs:** Look for specific error messages

## 💡 Pro Tips

- **Use virtual environments** to avoid conflicts
- **Keep pip updated** for better dependency resolution
- **Try minimal installation first** if you encounter issues
- **Use conda** as alternative to pip if available
- **Check firewall/proxy settings** if downloads fail

## 🔄 Update Instructions

To update the bot:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Need more help?** Check the main [README.md](README.md) or create an issue on GitHub. 