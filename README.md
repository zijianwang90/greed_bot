# CNN Fear & Greed Index Telegram Bot 📊

A Telegram bot that delivers daily CNN Fear & Greed Index updates and other US stock market sentiment indicators to help you stay informed about market sentiment.

## Features 🚀

- 📊 **Daily Fear & Greed Index Updates**: Get CNN's Fear & Greed Index delivered to your Telegram
- 📈 **Historical Data Comparison**: Compare current readings with past data
- 🔔 **Custom Notification Times**: Set your preferred time for daily updates
- 📱 **Interactive Commands**: Query current index and manage settings
- 📋 **Detailed Market Analysis**: Get insights into what's driving market sentiment
- 🌐 **Multi-language Support**: Available in English and Chinese
- ⏰ **Multiple Market Indicators**: 
  - CNN Fear & Greed Index
  - VIX Volatility Index
  - S&P 500 Momentum
  - Put/Call Ratio
  - Safe Haven Demand
  - Junk Bond Demand

## Market Sentiment Indicators 📈

The bot tracks multiple indicators to provide comprehensive market sentiment analysis:

1. **CNN Fear & Greed Index** (0-100 scale)
   - 0-24: Extreme Fear 😨
   - 25-49: Fear 😟
   - 50: Neutral 😐
   - 51-74: Greed 😃
   - 75-100: Extreme Greed 🤑

2. **VIX Volatility Index** - Market's "fear gauge"
3. **S&P 500 Momentum** - Relative to 125-day moving average
4. **Put/Call Ratio** - Options sentiment indicator
5. **Safe Haven Demand** - Stock vs bond performance
6. **Junk Bond Demand** - Risk appetite indicator

## Installation & Setup 🛠️

### 🚀 Automatic Installation (Recommended)

**Linux/macOS:**
```bash
git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot
install.bat
```

### 🔧 Manual Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/zijianwang90/greed_bot.git
   cd greed_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   **If you encounter dependency conflicts, try:**
   ```bash
   # Option 1: Use minimal dependencies
   pip install -r requirements-minimal.txt
   
   # Option 2: Upgrade pip first
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   
   # Option 3: Install core dependencies manually
   pip install python-telegram-bot requests aiohttp sqlalchemy apscheduler
   ```

3. **Set up configuration**:
   ```bash
   # Copy configuration templates
   cp config.example.py config.py
   cp config_local.example.py config_local.py
   
   # Edit your personal settings (Bot Token, Database, etc.)
   nano config_local.py
   ```

4. **Configure your Telegram Bot**:
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Get your bot token
   - Add the token to `config_local.py`

5. **Validate configuration (optional)**:
   ```bash
   python validate_config.py
   ```

6. **Run the bot**:
   ```bash
   python main.py
   ```

## Configuration 🔧

This project uses a two-file configuration system:

### Personal Settings (`config_local.py`)
Edit this file with your personal/secret configurations that don't change often:

```python
# Telegram Bot Token (required)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# Database Configuration
DATABASE_URL = "sqlite:///bot.db"  # For development
# DATABASE_URL = "postgresql://user:pass@host:port/db"  # For production

# Default notification time (24-hour format)
DEFAULT_NOTIFICATION_TIME = "09:00"

# Timezone
DEFAULT_TIMEZONE = "UTC"

# Admin settings
ADMIN_USER_ID = None  # Your Telegram user ID
```

### Business Settings (`config.py`)
This file contains business logic settings that might change during development:

```python
# Language settings
DEFAULT_LANGUAGE = "en"  # en, zh

# Feature toggles
ENABLE_HISTORICAL_DATA = True
ENABLE_VIX_DATA = True
ENABLE_MARKET_INDICATORS = True

# Update intervals (minutes)
DATA_UPDATE_INTERVAL = 60
NOTIFICATION_CHECK_INTERVAL = 1

# Rate limiting
RATE_LIMIT_MAX_REQUESTS = 20
```

### Benefits of This Structure:
- 🔒 **Personal settings** (tokens, passwords) stay in `config_local.py` (git-ignored)
- 🔄 **Business settings** can be updated via git without losing personal configs
- 📦 **Easy deployment** - just copy your `config_local.py` to new deployments

## Bot Commands 🤖

- `/start` - Start the bot and subscribe to daily updates
- `/current` - Get current Fear & Greed Index
- `/subscribe` - Subscribe to daily notifications
- `/unsubscribe` - Unsubscribe from notifications  
- `/settings` - Configure notification time and preferences
- `/history` - View historical data and trends
- `/help` - Show all available commands

## Usage Examples 💡

### Getting Started
1. Start a chat with your bot on Telegram
2. Send `/start` to begin
3. The bot will show you the current market sentiment
4. Set your preferred notification time with `/settings`

### Daily Notifications
The bot will send you daily updates like:

```
📊 **Market Sentiment Update**
🗓️ January 15, 2025

🎯 **CNN Fear & Greed Index: 73 (Greed)**
📈 Up 8 points from yesterday

📊 **Key Indicators:**
• VIX: 16.2 (-2.1%) 📉
• S&P 500 Momentum: Above 125-day MA ✅
• Put/Call Ratio: 0.65 (Bullish) 🐂
• Safe Haven: Stocks outperforming bonds ✅

🔍 **Analysis:**
Market showing signs of greed with low volatility and strong momentum. Options traders remain optimistic with more calls than puts being purchased.

📈 **7-day trend:** Fear → Neutral → Greed
```

## Project Structure 📁

```
greed_bot/
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
├── config.example.py      # Configuration template
├── config.py              # Your configuration (create from example)
├── bot/
│   ├── __init__.py
│   ├── handlers.py        # Telegram command handlers
│   ├── utils.py           # Utility functions
│   └── scheduler.py       # Job scheduling
├── data/
│   ├── __init__.py
│   ├── fetcher.py         # Data fetching from APIs
│   ├── models.py          # Database models
│   └── database.py        # Database operations
└── README.md
```

## Data Sources 📊

- **CNN Fear & Greed Index**: `https://production.dataviz.cnn.io/index/fearandgreed/graphdata/`
- **VIX Data**: Yahoo Finance API
- **Market Data**: Multiple financial APIs with fallback options

## Features in Detail 🔍

### Smart Scheduling
- Respects user time zones
- Handles market holidays
- Configurable notification times per user

### Data Reliability
- Multiple data source fallbacks
- Error handling and retry logic
- Historical data validation

### User Experience
- Interactive inline keyboards
- Rich formatting with emojis
- Multi-language support
- Personalized settings

## Deployment 🚀

### Heroku Deployment
1. Create a Heroku app
2. Set environment variables
3. Deploy with Git
4. Enable worker dyno

### Docker Deployment
```dockerfile
# Dockerfile included in project
docker build -t greed-bot .
docker run -d --env-file .env greed-bot
```

### VPS Deployment
1. Set up Python environment
2. Configure systemd service
3. Set up reverse proxy (optional)
4. Configure SSL certificates

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting 🔧

### Installation Issues

**Dependency Conflicts:**
```bash
# Try installing with minimal dependencies first
pip install -r requirements-minimal.txt

# If cryptography fails on macOS:
brew install openssl libffi
export LDFLAGS="-L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
pip install cryptography

# If cryptography fails on Ubuntu/Debian:
sudo apt-get update
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev
pip install cryptography

# For Windows users having issues:
pip install --upgrade pip setuptools wheel
pip install --only-binary=all cryptography
```

**Python Version Issues:**
- Ensure you're using Python 3.8 or higher
- Some packages may require Python < 3.12

### Common Runtime Issues
- **Bot not responding**: Check token and internet connection
- **No data updates**: Verify API endpoints are accessible  
- **Database errors**: Check database connection and permissions
- **Scheduling issues**: Verify timezone settings

### Debug Mode
Enable debug logging in `config.py`:
```python
DEBUG = True
LOG_LEVEL = "DEBUG"
```

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚠️

This bot is for informational purposes only. The Fear & Greed Index and other market indicators should not be used as the sole basis for investment decisions. Always do your own research and consider consulting with financial professionals.

## Acknowledgments 🙏

- CNN for providing the Fear & Greed Index
- Telegram Bot API
- All contributors and users

---

**Happy Trading! 📈🤖** 