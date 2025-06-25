@echo off
echo 🤖 Fear & Greed Index Bot Installation Script (Windows)
echo ====================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

:: Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

:: Try to install dependencies
echo 📥 Installing dependencies...

:: First try full requirements
python -m pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo ✅ All dependencies installed successfully!
    goto config_setup
)

echo ⚠️ Full installation failed, trying minimal dependencies...

:: If full installation fails, try minimal
python -m pip install -r requirements-minimal.txt
if %errorlevel% equ 0 (
    echo ✅ Minimal dependencies installed successfully!
    echo ⚠️ Some optional features may not be available
    goto config_setup
)

echo ❌ Minimal installation also failed
echo 🔧 Trying to install core dependencies manually...

:: Manual installation of core dependencies
python -m pip install python-telegram-bot requests aiohttp sqlalchemy apscheduler pandas beautifulsoup4 python-dotenv

echo ✅ Core dependencies installed
echo ⚠️ Some features may be limited

:config_setup
:: Create config file if it doesn't exist
if not exist "config.py" (
    echo ⚙️ Creating configuration file...
    copy config.example.py config.py
    echo ✅ Config file created from template
    echo 📝 Please edit config.py with your bot token and settings
) else (
    echo ✅ Configuration file already exists
)

echo.
echo 🎉 Installation completed!
echo.
echo Next steps:
echo 1. Edit config.py with your Telegram bot token
echo 2. Run: python main.py
echo.
echo For troubleshooting, see the README.md file
pause 