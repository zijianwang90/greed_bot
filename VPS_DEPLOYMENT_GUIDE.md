# 🚀 CNN恐慌贪婪指数Bot - VPS部署完整指南

> **⚡ 快速部署**: 运行一键部署脚本 `curl -sSL https://raw.githubusercontent.com/zijianwang90/greed_bot/main/install.sh | bash`
> 
> **📋 重要**: 部署完成后请编辑 `config_local.py` 设置您的Bot Token

## 📋 部署前准备

### 💻 系统要求
- **操作系统**: Ubuntu 18.04+ / CentOS 7+ / Debian 9+ / RHEL 8+
- **Python版本**: Python 3.8+ (推荐 Python 3.9+)
- **内存要求**: 最少 512MB RAM (推荐 1GB+)
- **磁盘空间**: 最少 1GB (推荐 2GB+)
- **网络**: 稳定的互联网连接，能访问 Telegram API

### 🛠️ 1. 系统环境准备

#### Ubuntu/Debian 系统
```bash
# 更新包列表
sudo apt-get update && sudo apt-get upgrade -y

# 安装必需依赖
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    screen \
    htop \
    sqlite3 \
    build-essential \
    libssl-dev \
    libffi-dev

# 验证Python版本
python3 --version
```

#### CentOS/RHEL 系统
```bash
# 更新系统
sudo yum update -y

# 安装EPEL仓库 (CentOS 7)
sudo yum install -y epel-release

# 安装依赖
sudo yum install -y \
    python3 \
    python3-pip \
    python3-devel \
    git \
    curl \
    wget \
    screen \
    htop \
    sqlite \
    gcc \
    gcc-c++ \
    make \
    openssl-devel \
    libffi-devel

# 验证Python版本
python3 --version
```

### 🔧 2. 获取Telegram Bot Token

1. 在Telegram中联系 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建新bot
3. 按提示设置bot名称和用户名
4. 保存获得的token (格式: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`)
5. 可选：通过 [@userinfobot](https://t.me/userinfobot) 获取您的用户ID (用于管理员权限)

## 📦 部署步骤

### 🚀 方法1: 一键自动部署 (推荐)

```bash
# 下载并运行一键部署脚本
curl -sSL https://raw.githubusercontent.com/zijianwang90/greed_bot/main/install.sh | bash

# 或者手动下载后执行
wget https://raw.githubusercontent.com/zijianwang90/greed_bot/main/install.sh
chmod +x install.sh
./install.sh
```

### 📥 方法2: 手动部署

#### 1. 克隆项目
```bash
# 创建项目目录
sudo mkdir -p /opt/greed_bot
cd /opt

# 克隆项目 (确保替换为正确的仓库地址)
sudo git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot

# 设置目录权限
sudo chown -R $USER:$USER /opt/greed_bot
chmod 755 /opt/greed_bot
```

#### 2. 安装Python依赖
```bash
cd /opt/greed_bot

# 运行安装脚本
chmod +x install.sh
./install.sh

# 或手动安装
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 3. 配置Bot设置

**🔑 创建配置文件**
```bash
# 复制配置模板
cp config_local.example.py config_local.py

# 编辑配置文件
nano config_local.py
```

**⚙️ 必填配置项**
```python
# config_local.py

# 🤖 Telegram Bot Token (必填)
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrSTUvwxyz"

# 🗄️ 数据库配置 (SQLite - 推荐VPS使用)
DATABASE_URL = "sqlite:////opt/greed_bot/bot.db"

# 🕐 通知设置
DEFAULT_NOTIFICATION_TIME = "09:00"
DEFAULT_TIMEZONE = "Asia/Shanghai"  # 或 "UTC", "America/New_York" 等

# 👤 管理员设置 (可选，用于管理命令)
ADMIN_USER_ID = 123456789  # 您的Telegram用户ID

# 📝 日志设置
LOG_LEVEL = "INFO"
LOG_FILE = "/opt/greed_bot/bot.log"
LOG_TO_CONSOLE = True

# 🐛 开发设置
DEBUG = False
TEST_MODE = False
```

**🔍 验证配置**
```bash
# 验证配置文件语法和必要设置
python validate_config.py

# 如果验证成功，会显示：
# ✅ 配置验证通过!
# 🚀 您可以运行 './start_bot.sh' 或 'python main.py' 启动Bot
```

## 💾 数据库配置说明

### 🗃️ SQLite 数据库 (推荐VPS使用)

**✅ 优势**: 零配置、轻量级、无需额外服务
**重要**: SQLite是文件数据库，**不需要启动任何数据库服务**！

Bot运行时会自动：
1. 创建数据库文件（如果不存在）
2. 创建必要的数据表结构
3. 处理所有数据库读写操作

**🔧 配置示例**:
```python
# 相对路径 (开发测试)
DATABASE_URL = "sqlite:///bot.db"

# 绝对路径 (生产推荐)
DATABASE_URL = "sqlite:////opt/greed_bot/bot.db"
```

**📂 数据库文件管理**:
```bash
# 查看数据库文件
ls -la /opt/greed_bot/bot.db

# 设置合适的权限
chmod 755 /opt/greed_bot/
chmod 644 /opt/greed_bot/bot.db  # 文件创建后

# 备份数据库
cp /opt/greed_bot/bot.db /opt/greed_bot/backup/bot.db.$(date +%Y%m%d_%H%M%S)
```

### 🐘 PostgreSQL 数据库 (企业级选项)

**📋 适用场景**: 高并发、大量用户、多实例部署

**🛠️ 安装PostgreSQL**:
```bash
# Ubuntu/Debian
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE greed_bot;
CREATE USER bot_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE greed_bot TO bot_user;
\q
```

**⚙️ 配置示例**:
```python
# PostgreSQL 配置
DATABASE_URL = "postgresql://bot_user:your_secure_password@localhost:5432/greed_bot"
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
```

## 🚀 启动Bot

### 🧪 方法1: 前台测试运行

**适用**: 初次部署测试、开发调试

```bash
cd /opt/greed_bot

# 激活虚拟环境
source venv/bin/activate

# 直接启动 (前台运行)
python main.py

# 或使用便捷脚本
./start_bot.sh
```

**🔍 查看输出**: 正常启动应该看到类似信息：
```
🤖 Starting Fear & Greed Index Bot...
✅ Virtual environment activated
✅ Configuration validated
🚀 Bot started successfully
📊 Fetching Fear & Greed Index data...
🟢 Bot is running and ready to receive commands
```

### 📺 方法2: Screen 后台运行

**适用**: 简单后台运行，易于查看和调试

```bash
cd /opt/greed_bot

# 创建新的screen会话
screen -S greed_bot

# 在screen中启动bot
source venv/bin/activate
python main.py

# 退出screen保持bot运行: 按 Ctrl+A, 然后按 D
# 重新连接: screen -r greed_bot
# 列出所有screen: screen -ls
# 终止screen: screen -X -S greed_bot quit
```

### ⚙️ 方法3: Systemd 服务 (生产推荐)

**适用**: 生产环境，自动启动，稳定运行

#### 🔧 创建服务文件
```bash
sudo tee /etc/systemd/system/greed-bot.service > /dev/null << EOF
[Unit]
Description=CNN Fear & Greed Index Telegram Bot
Documentation=https://github.com/zijianwang90/greed_bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/opt/greed_bot
Environment=PATH=/opt/greed_bot/venv/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/greed_bot
ExecStart=/opt/greed_bot/venv/bin/python /opt/greed_bot/main.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
TimeoutSec=30

# 安全设置
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/greed_bot

# 日志设置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=greed-bot

[Install]
WantedBy=multi-user.target
EOF
```

#### 🎯 启动和管理服务
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable greed-bot

# 启动服务
sudo systemctl start greed-bot

# 查看服务状态
sudo systemctl status greed-bot

# 停止服务
sudo systemctl stop greed-bot

# 重启服务  
sudo systemctl restart greed-bot

# 禁用开机自启
sudo systemctl disable greed-bot
```

#### 📋 查看日志
```bash
# 实时查看日志
sudo journalctl -u greed-bot -f

# 查看最近日志
sudo journalctl -u greed-bot --since "1 hour ago"

# 查看错误日志
sudo journalctl -u greed-bot --since today | grep ERROR

# 导出日志到文件
sudo journalctl -u greed-bot --since "2024-01-01" > greed_bot.log
```

### 🐳 方法4: Docker运行 (高级选项)

**适用**: 容器化部署，环境隔离

```bash
# 构建Docker镜像
docker build -t greed-bot .

# 运行容器
docker run -d \
  --name greed-bot \
  --restart unless-stopped \
  -v /opt/greed_bot/config_local.py:/app/config_local.py:ro \
  -v /opt/greed_bot/data:/app/data \
  greed-bot

# 查看容器状态
docker ps | grep greed-bot

# 查看容器日志
docker logs -f greed-bot
```

## 📊 监控和维护

### 🔍 检查Bot运行状态

#### 基本状态检查
```bash
# 检查Bot进程
ps aux | grep python | grep main.py

# 检查systemd服务状态
sudo systemctl status greed-bot

# 检查端口占用（如果启用webhook）
sudo netstat -tlnp | grep :8443

# 检查系统资源使用
htop  # 或 top
```

#### 健康状态验证
```bash
# 检查日志中的错误
sudo journalctl -u greed-bot --since "1 hour ago" | grep -E "(ERROR|CRITICAL|FAILED)"

# 查看最近启动信息  
sudo journalctl -u greed-bot --since today | grep -E "(Started|starting)"

# 检查网络连接
curl -I https://api.telegram.org/bot<YOUR_TOKEN>/getMe
curl -I https://production.dataviz.cnn.io/index/fearandgreed/graphdata
```

### 💾 数据库管理

#### SQLite 数据库维护
```bash
# 查看数据库信息
ls -lh /opt/greed_bot/bot.db
file /opt/greed_bot/bot.db

# 创建备份目录
mkdir -p /opt/greed_bot/backup

# 自动备份脚本
cat > /opt/greed_bot/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/greed_bot/backup"
DB_FILE="/opt/greed_bot/bot.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/bot_backup_$TIMESTAMP.db"

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "✅ Database backed up to: $BACKUP_FILE"
    
    # 保留最近7天的备份
    find "$BACKUP_DIR" -name "bot_backup_*.db" -mtime +7 -delete
    echo "🧹 Cleaned old backups (>7 days)"
else
    echo "❌ Database file not found: $DB_FILE"
fi
EOF

chmod +x /opt/greed_bot/backup_db.sh

# 手动备份
./backup_db.sh

# 检查数据库完整性
sqlite3 /opt/greed_bot/bot.db "PRAGMA integrity_check;"

# 查看数据库统计
sqlite3 /opt/greed_bot/bot.db "
SELECT 
    name,
    COUNT(*) as record_count 
FROM sqlite_master 
WHERE type='table' 
GROUP BY name;
"
```

#### 自动化备份 (Crontab)
```bash
# 添加每日备份任务
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * /opt/greed_bot/backup_db.sh >> /opt/greed_bot/backup.log 2>&1
```

### 🔄 更新和升级

#### Bot代码更新
```bash
cd /opt/greed_bot

# 停止Bot服务
sudo systemctl stop greed-bot

# 备份当前配置
cp config_local.py config_local.py.backup.$(date +%Y%m%d)

# 拉取最新代码
git stash  # 暂存本地修改
git pull origin main
git stash pop  # 恢复本地修改

# 更新依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 运行数据库迁移（如果有）
python migrate_db.py

# 验证配置
python validate_config.py

# 重启服务
sudo systemctl start greed-bot
sudo systemctl status greed-bot
```

#### 依赖更新
```bash
cd /opt/greed_bot
source venv/bin/activate

# 查看过期包
pip list --outdated

# 安全更新（只更新补丁版本）
pip install --upgrade $(pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1)

# 测试更新后的功能
python -c "import config; print('✅ Config import OK')"
```

### 📈 性能监控

#### 系统资源监控
```bash
# 创建监控脚本
cat > /opt/greed_bot/monitor.sh << 'EOF'
#!/bin/bash
echo "=== Bot监控报告 $(date) ==="

# 进程状态
if pgrep -f "python.*main.py" > /dev/null; then
    echo "✅ Bot进程运行中"
    PID=$(pgrep -f "python.*main.py")
    echo "📍 进程ID: $PID"
    
    # 内存使用
    echo "💾 内存使用: $(ps -p $PID -o rss= | awk '{print $1/1024 " MB"}')"
    
    # CPU使用
    echo "⚡ CPU使用: $(ps -p $PID -o %cpu= | awk '{print $1"%"}')"
else
    echo "❌ Bot进程未运行"
fi

# 磁盘空间
echo "💿 磁盘使用: $(df -h /opt/greed_bot | tail -1 | awk '{print $5}')"

# 数据库大小
if [ -f "/opt/greed_bot/bot.db" ]; then
    echo "🗄️ 数据库大小: $(du -h /opt/greed_bot/bot.db | cut -f1)"
fi

# 最近错误日志
ERROR_COUNT=$(sudo journalctl -u greed-bot --since "1 hour ago" | grep -c ERROR)
echo "⚠️ 近1小时错误数: $ERROR_COUNT"

echo "=========================="
EOF

chmod +x /opt/greed_bot/monitor.sh

# 运行监控
./monitor.sh
```

#### 日志分析
```bash
# 创建日志分析脚本
cat > /opt/greed_bot/log_analysis.sh << 'EOF'
#!/bin/bash
echo "=== Bot日志分析 $(date) ==="

# 错误统计
echo "📊 近24小时错误统计:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep ERROR | wc -l

# 用户活动统计  
echo "👥 近24小时用户消息:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -c "user_id"

# API请求统计
echo "🌐 近24小时API请求:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -c "API request"

# 重启次数
echo "🔄 近24小时重启次数:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -c "Started"

echo "=========================="
EOF

chmod +x /opt/greed_bot/log_analysis.sh
```

## 🔧 故障排除和常见问题

### 🚨 紧急故障排除

#### 快速诊断脚本
```bash
# 创建一键诊断脚本
cat > /opt/greed_bot/diagnose.sh << 'EOF'
#!/bin/bash
echo "🔍 Bot故障诊断工具"
echo "=================="

# 1. 检查服务状态
echo "1️⃣ 检查服务状态:"
if systemctl is-active --quiet greed-bot; then
    echo "✅ Systemd服务运行中"
else
    echo "❌ Systemd服务未运行"
fi

# 2. 检查进程
echo -e "\n2️⃣ 检查进程:"
if pgrep -f "python.*main.py" > /dev/null; then
    PID=$(pgrep -f "python.*main.py")
    echo "✅ Bot进程运行中 (PID: $PID)"
else
    echo "❌ Bot进程未运行"
fi

# 3. 检查配置文件
echo -e "\n3️⃣ 检查配置文件:"
for file in config_local.py config.py; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
    fi
done

# 4. 检查虚拟环境
echo -e "\n4️⃣ 检查虚拟环境:"
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "✅ 虚拟环境正常"
else
    echo "❌ 虚拟环境异常"
fi

# 5. 检查网络连接
echo -e "\n5️⃣ 检查网络连接:"
if curl -s --connect-timeout 5 https://api.telegram.org > /dev/null; then
    echo "✅ Telegram API 可达"
else
    echo "❌ Telegram API 不可达"
fi

if curl -s --connect-timeout 5 https://production.dataviz.cnn.io > /dev/null; then
    echo "✅ CNN API 可达"
else
    echo "❌ CNN API 不可达"
fi

# 6. 检查磁盘空间
echo -e "\n6️⃣ 检查磁盘空间:"
DISK_USAGE=$(df /opt/greed_bot | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 90 ]; then
    echo "✅ 磁盘空间充足 ($DISK_USAGE%)"
else
    echo "⚠️ 磁盘空间不足 ($DISK_USAGE%)"
fi

# 7. 检查最近错误
echo -e "\n7️⃣ 最近错误统计:"
ERROR_COUNT=$(sudo journalctl -u greed-bot --since "1 hour ago" 2>/dev/null | grep -c ERROR || echo "0")
echo "⚠️ 近1小时错误数: $ERROR_COUNT"

echo -e "\n=================="
echo "诊断完成"
EOF

chmod +x /opt/greed_bot/diagnose.sh

# 运行诊断
./diagnose.sh
```

### 🐛 常见问题详解

#### ❌ 问题1: Bot无法启动

**🔍 症状**:
- `systemctl start greed-bot` 失败
- 进程无法启动
- 配置验证失败

**🔧 解决方案**:
```bash
# Step 1: 检查配置文件语法
cd /opt/greed_bot
source venv/bin/activate
python validate_config.py

# Step 2: 检查Bot Token
python3 -c "
import config_local
import requests
token = config_local.TELEGRAM_BOT_TOKEN
response = requests.get(f'https://api.telegram.org/bot{token}/getMe')
print('✅ Token valid' if response.status_code == 200 else '❌ Token invalid')
"

# Step 3: 检查依赖
pip check

# Step 4: 重新安装依赖
pip install --force-reinstall -r requirements-minimal.txt

# Step 5: 手动测试启动
python main.py
```

#### ❌ 问题2: 导入配置失败

**🔍 症状**:
```
ImportError: No module named 'config_local'
ModuleNotFoundError: No module named 'config'
```

**🔧 解决方案**:
```bash
# 检查配置文件是否存在
ls -la config*.py

# 创建缺失的配置文件
if [ ! -f "config_local.py" ]; then
    cp config_local.example.py config_local.py
    echo "📝 请编辑 config_local.py 添加您的Bot Token"
fi

# 检查文件权限
chmod 644 config*.py

# 验证Python路径
python3 -c "import sys; print(sys.path)"
```

#### ❌ 问题3: 数据库连接错误

**🔍 症状**:
```
sqlite3.OperationalError: unable to open database file
PermissionError: [Errno 13] Permission denied
```

**🔧 解决方案**:
```bash
# 检查数据库目录权限
ls -la /opt/greed_bot/

# 创建数据库目录
mkdir -p /opt/greed_bot/data

# 修复权限
sudo chown -R $USER:$USER /opt/greed_bot/
chmod 755 /opt/greed_bot/
chmod 644 /opt/greed_bot/*.db 2>/dev/null || true

# 测试数据库连接
python3 -c "
import sqlite3
import config_local
db_url = config_local.DATABASE_URL.replace('sqlite:///', '')
try:
    conn = sqlite3.connect(db_url)
    conn.close()
    print('✅ Database connection OK')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

#### ❌ 问题4: 网络连接超时

**🔍 症状**:
```
requests.exceptions.ConnectTimeout
requests.exceptions.ReadTimeout
```

**🔧 解决方案**:
```bash
# 检查DNS解析
nslookup api.telegram.org
nslookup production.dataviz.cnn.io

# 检查防火墙规则
sudo iptables -L | grep -E "(DROP|REJECT)"

# 测试网络连接
curl -v --connect-timeout 10 https://api.telegram.org/bot123/getMe
curl -v --connect-timeout 10 https://production.dataviz.cnn.io/index/fearandgreed/graphdata

# 设置代理（如果需要）
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="http://proxy:port"

# 检查系统时间（重要！）
timedatectl status
```

#### ❌ 问题5: 内存不足

**🔍 症状**:
```
MemoryError
OSError: [Errno 12] Cannot allocate memory
```

**🔧 解决方案**:
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 检查交换空间
swapon --show

# 创建交换文件（如果没有）
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用交换
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 重启低内存服务
sudo systemctl restart greed-bot
```

#### ❌ 问题6: Systemd服务问题

**🔍 症状**:
- 服务频繁重启
- 服务启动失败
- 权限问题

**🔧 解决方案**:
```bash
# 检查服务状态详情
sudo systemctl status greed-bot -l

# 查看详细错误日志
sudo journalctl -u greed-bot -n 50

# 重新创建服务文件
sudo systemctl stop greed-bot
sudo systemctl disable greed-bot

# 删除旧服务文件
sudo rm -f /etc/systemd/system/greed-bot.service

# 重新创建服务文件（使用上面的systemd配置）
# ... [参考前面的systemd配置]

# 重新加载和启动
sudo systemctl daemon-reload
sudo systemctl enable greed-bot
sudo systemctl start greed-bot
```

### 📊 日志分析和调试

#### 高级日志分析
```bash
# 创建日志分析工具
cat > /opt/greed_bot/log_debug.sh << 'EOF'
#!/bin/bash
echo "🔍 Bot日志调试工具"
echo "=================="

# 检查不同级别的日志
echo "📊 日志级别统计:"
sudo journalctl -u greed-bot --since "24 hours ago" | \
awk '/DEBUG/{debug++} /INFO/{info++} /WARNING/{warn++} /ERROR/{error++} /CRITICAL/{critical++} 
END {
    print "DEBUG: " (debug+0)
    print "INFO: " (info+0) 
    print "WARNING: " (warn+0)
    print "ERROR: " (error+0)
    print "CRITICAL: " (critical+0)
}'

echo -e "\n🔥 最近错误详情:"
sudo journalctl -u greed-bot --since "1 hour ago" | grep -A3 -B1 ERROR | tail -20

echo -e "\n📈 启动信息:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -E "(Starting|Started|Stopping)" | tail -10

echo -e "\n🌐 网络请求统计:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -c "requests" || echo "0"

echo -e "\n💾 数据库操作:"
sudo journalctl -u greed-bot --since "24 hours ago" | grep -c "database\|SQL" || echo "0"

echo "=================="
EOF

chmod +x /opt/greed_bot/log_debug.sh
```

#### 启用调试模式
```bash
# 临时启用调试模式
echo "# 临时调试配置
DEBUG = True
LOG_LEVEL = 'DEBUG'
" >> config_local.py

# 重启服务查看详细日志
sudo systemctl restart greed-bot
sudo journalctl -u greed-bot -f

# 完成调试后恢复
sed -i '/# 临时调试配置/,$d' config_local.py
```

## 🔒 安全加固

### 🛡️ 防火墙配置

#### Ubuntu/Debian (UFW)
```bash
# 启用基本防火墙
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许SSH（根据实际端口调整）
sudo ufw allow ssh
# 或指定端口: sudo ufw allow 22/tcp

# 如果使用Webhook模式，开放相应端口
# sudo ufw allow 8443/tcp
# sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw --force enable

# 查看状态
sudo ufw status verbose
```

#### CentOS/RHEL (firewalld)
```bash
# 检查firewalld状态
sudo systemctl status firewalld

# 启动firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 设置默认区域
sudo firewall-cmd --set-default-zone=public

# 允许SSH
sudo firewall-cmd --permanent --add-service=ssh

# 如果使用Webhook
# sudo firewall-cmd --permanent --add-port=8443/tcp
# sudo firewall-cmd --permanent --add-port=443/tcp

# 重载配置
sudo firewall-cmd --reload

# 查看配置
sudo firewall-cmd --list-all
```

### 🔐 文件权限安全

```bash
# 设置安全的目录权限
sudo chown -R $USER:$USER /opt/greed_bot/
chmod 755 /opt/greed_bot/

# 保护敏感配置文件
chmod 600 /opt/greed_bot/config_local.py
chmod 600 /opt/greed_bot/*.log 2>/dev/null || true

# 数据库文件权限
chmod 644 /opt/greed_bot/bot.db 2>/dev/null || true

# 脚本文件权限
chmod 755 /opt/greed_bot/*.sh

# 移除其他用户对敏感文件的访问
find /opt/greed_bot -name "*.py" -exec chmod o-rwx {} \;
```

### 🔒 系统安全强化

#### 创建专用用户（推荐）
```bash
# 创建专用的greed-bot用户
sudo useradd -r -s /bin/false -d /opt/greed_bot greed-bot

# 设置目录所有者
sudo chown -R greed-bot:greed-bot /opt/greed_bot/

# 更新systemd服务文件使用专用用户
sudo sed -i 's/User=.*/User=greed-bot/' /etc/systemd/system/greed-bot.service
sudo sed -i 's/Group=.*/Group=greed-bot/' /etc/systemd/system/greed-bot.service

# 重载并重启服务
sudo systemctl daemon-reload
sudo systemctl restart greed-bot
```

#### SSH安全配置
```bash
# 备份SSH配置
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# 安全配置建议
sudo tee -a /etc/ssh/sshd_config << EOF

# 安全配置
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

# 重启SSH服务
sudo systemctl restart sshd
```

### 🔍 监控和日志安全

#### 日志轮转配置
```bash
# 创建日志轮转配置
sudo tee /etc/logrotate.d/greed-bot << EOF
/opt/greed_bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su greed-bot greed-bot
}
EOF

# 测试配置
sudo logrotate -d /etc/logrotate.d/greed-bot
```

#### 入侵检测设置
```bash
# 安装fail2ban
sudo apt-get install -y fail2ban  # Ubuntu/Debian
# sudo yum install -y fail2ban     # CentOS/RHEL

# 创建greed-bot的fail2ban配置
sudo tee /etc/fail2ban/jail.local << EOF
[greed-bot]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

# 启动fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📈 性能优化

### ⚡ 系统级优化

#### 内核参数调优
```bash
# 创建系统优化配置
sudo tee /etc/sysctl.d/99-greed-bot.conf << EOF
# 网络性能优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216

# 文件描述符限制
fs.file-max = 100000

# 内存管理
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
EOF

# 应用配置
sudo sysctl -p /etc/sysctl.d/99-greed-bot.conf
```

#### 用户限制优化
```bash
# 增加用户进程和文件限制
sudo tee -a /etc/security/limits.conf << EOF
# Greed Bot limits
greed-bot soft nofile 65536
greed-bot hard nofile 65536
greed-bot soft nproc 4096
greed-bot hard nproc 4096
EOF
```

### 🐍 Python性能优化

#### 配置文件优化
```python
# 在 config_local.py 中添加性能配置

# 🚀 性能优化设置
# 数据更新频率（分钟）- 根据用户数量调整
DATA_UPDATE_INTERVAL = 60  # 少用户: 120, 多用户: 30

# HTTP请求优化
REQUEST_TIMEOUT = 15  # 减少超时时间
MAX_RETRIES = 2       # 减少重试次数

# 缓存设置
ENABLE_CACHING = True
CACHE_TTL = 600       # 10分钟缓存

# 数据库优化
DB_POOL_SIZE = 5      # SQLite建议较小
DB_MAX_OVERFLOW = 10

# 限制并发
MAX_CONCURRENT_REQUESTS = 5

# 内存优化
HISTORICAL_DAYS = 7   # 减少历史数据天数
```

#### Python环境优化
```bash
# 安装性能优化包
source /opt/greed_bot/venv/bin/activate
pip install uvloop  # 更快的事件循环（Linux）

# 设置Python优化环境变量
echo 'export PYTHONOPTIMIZE=1' >> ~/.bashrc
echo 'export PYTHONDONTWRITEBYTECODE=1' >> ~/.bashrc

# 更新systemd服务添加优化变量
sudo sed -i '/\[Service\]/a Environment=PYTHONOPTIMIZE=1' /etc/systemd/system/greed-bot.service
sudo sed -i '/Environment=PYTHONOPTIMIZE=1/a Environment=PYTHONDONTWRITEBYTECODE=1' /etc/systemd/system/greed-bot.service

sudo systemctl daemon-reload
sudo systemctl restart greed-bot
```

### 📊 监控性能指标

#### 创建性能监控脚本
```bash
cat > /opt/greed_bot/performance_monitor.sh << 'EOF'
#!/bin/bash
echo "📊 Greed Bot 性能监控报告"
echo "时间: $(date)"
echo "=================================="

# Bot进程信息
PID=$(pgrep -f "python.*main.py")
if [ -n "$PID" ]; then
    echo "🔍 进程信息:"
    echo "  PID: $PID"
    echo "  内存使用: $(ps -p $PID -o rss= | awk '{printf "%.1f MB", $1/1024}')"
    echo "  CPU使用: $(ps -p $PID -o %cpu=)%"
    echo "  运行时间: $(ps -p $PID -o etime=)"
    
    # 文件描述符使用
    FD_COUNT=$(ls /proc/$PID/fd 2>/dev/null | wc -l)
    echo "  文件描述符: $FD_COUNT"
    
    # 线程数
    THREAD_COUNT=$(ps -p $PID -o nlwp=)
    echo "  线程数: $THREAD_COUNT"
fi

echo -e "\n💾 系统资源:"
echo "  总内存: $(free -h | awk '/^Mem/ {print $2}')"
echo "  已用内存: $(free -h | awk '/^Mem/ {print $3}')"
echo "  内存使用率: $(free | awk '/^Mem/ {printf "%.1f%%", $3/$2*100}')"

echo -e "\n💿 磁盘使用:"
df -h /opt/greed_bot | tail -1 | awk '{print "  使用空间: " $3 "/" $2 " (" $5 ")"}'

echo -e "\n🌐 网络连接:"
CONNECTIONS=$(ss -tn | grep ESTAB | wc -l)
echo "  建立连接数: $CONNECTIONS"

echo -e "\n📈 最近24小时统计:"
if command -v journalctl >/dev/null 2>&1; then
    REQUESTS=$(sudo journalctl -u greed-bot --since "24 hours ago" 2>/dev/null | grep -c "request" || echo "0")
    ERRORS=$(sudo journalctl -u greed-bot --since "24 hours ago" 2>/dev/null | grep -c "ERROR" || echo "0")
    echo "  API请求: $REQUESTS"
    echo "  错误数: $ERRORS"
fi

echo "=================================="
EOF

chmod +x /opt/greed_bot/performance_monitor.sh

# 设置定期监控
echo "0 */6 * * * /opt/greed_bot/performance_monitor.sh >> /opt/greed_bot/performance.log 2>&1" | crontab -
```

## 🏃‍♂️ 一键部署脚本

### 🚀 完整自动化部署

```bash
# 创建完整的一键部署脚本
curl -sSL https://raw.githubusercontent.com/zijianwang90/greed_bot/main/install.sh | bash

# 或手动创建脚本
cat > /tmp/greed_bot_deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "🤖 CNN Fear & Greed Index Bot - 一键部署脚本"
echo "=============================================="

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要以root用户运行此脚本"
    echo "💡 使用: bash $0"
    exit 1
fi

# 检查操作系统
if command -v apt-get >/dev/null 2>&1; then
    OS="ubuntu"
    echo "✅ 检测到 Ubuntu/Debian 系统"
elif command -v yum >/dev/null 2>&1; then
    OS="centos"
    echo "✅ 检测到 CentOS/RHEL 系统"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 1. 更新系统并安装依赖
echo "📦 安装系统依赖..."
if [ "$OS" = "ubuntu" ]; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv python3-dev git curl wget screen htop sqlite3 build-essential libssl-dev libffi-dev
else
    sudo yum update -y
    sudo yum install -y epel-release
    sudo yum install -y python3 python3-pip python3-devel git curl wget screen htop sqlite gcc gcc-c++ make openssl-devel libffi-devel
fi

# 2. 克隆项目
echo "📥 下载项目代码..."
sudo mkdir -p /opt/greed_bot
cd /opt
if [ -d "greed_bot" ]; then
    echo "⚠️ 项目目录已存在，备份旧版本..."
    sudo mv greed_bot greed_bot.backup.$(date +%Y%m%d_%H%M%S)
fi

sudo git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot
sudo chown -R $USER:$USER /opt/greed_bot

# 3. 安装Python依赖
echo "🐍 安装Python依赖..."
chmod +x install.sh
./install.sh

# 4. 创建配置文件
echo "⚙️ 创建配置文件..."
if [ ! -f "config_local.py" ]; then
    cp config_local.example.py config_local.py
    echo "✅ 配置文件已创建"
else
    echo "⚠️ 配置文件已存在，跳过创建"
fi

# 5. 创建systemd服务
echo "🔧 设置系统服务..."
sudo tee /etc/systemd/system/greed-bot.service > /dev/null << SERVICE_EOF
[Unit]
Description=CNN Fear & Greed Index Telegram Bot
Documentation=https://github.com/zijianwang90/greed_bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/opt/greed_bot
Environment=PATH=/opt/greed_bot/venv/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/greed_bot
Environment=PYTHONOPTIMIZE=1
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart=/opt/greed_bot/venv/bin/python /opt/greed_bot/main.py
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
TimeoutSec=30

# 安全设置
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/greed_bot

# 日志设置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=greed-bot

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 6. 创建管理脚本
echo "📜 创建管理脚本..."
chmod +x *.sh 2>/dev/null || true

# 7. 设置文件权限
echo "🔒 设置安全权限..."
chmod 600 config_local.py
chmod 755 /opt/greed_bot

# 8. 重载systemd
sudo systemctl daemon-reload
sudo systemctl enable greed-bot

echo ""
echo "🎉 部署完成！"
echo ""
echo "📋 接下来的步骤:"
echo "1. 编辑配置文件: nano /opt/greed_bot/config_local.py"
echo "   - 设置您的 TELEGRAM_BOT_TOKEN"
echo "   - 调整其他配置（可选）"
echo ""
echo "2. 验证配置: cd /opt/greed_bot && python validate_config.py"
echo ""
echo "3. 启动Bot:"
echo "   - 测试启动: cd /opt/greed_bot && ./start_bot.sh"
echo "   - 服务启动: sudo systemctl start greed-bot"
echo "   - 查看状态: sudo systemctl status greed-bot"
echo "   - 查看日志: sudo journalctl -u greed-bot -f"
echo ""
echo "📚 更多信息请查看: /opt/greed_bot/VPS_DEPLOYMENT_GUIDE.md"
echo ""
EOF

chmod +x /tmp/greed_bot_deploy.sh

# 运行部署脚本
echo "🚀 开始自动部署..."
/tmp/greed_bot_deploy.sh
```

### 📋 快速命令参考

#### 🔧 常用管理命令
```bash
# 进入项目目录
cd /opt/greed_bot

# 查看服务状态
sudo systemctl status greed-bot

# 启动/停止/重启服务
sudo systemctl start greed-bot
sudo systemctl stop greed-bot
sudo systemctl restart greed-bot

# 查看实时日志
sudo journalctl -u greed-bot -f

# 验证配置
python validate_config.py

# 手动启动测试
./start_bot.sh

# 更新代码
git pull && sudo systemctl restart greed-bot

# 备份数据库
./backup_db.sh

# 性能监控
./monitor.sh

# 故障诊断
./diagnose.sh
```

#### 🆘 紧急故障恢复
```bash
# 快速重置和重启
sudo systemctl stop greed-bot
cd /opt/greed_bot
git stash
git pull
source venv/bin/activate
pip install -r requirements-minimal.txt
python validate_config.py
sudo systemctl start greed-bot
sudo systemctl status greed-bot
```

---

## 🎯 部署检查清单

### ✅ 部署完成检查

#### 🔍 基础检查
- [ ] ✅ Python 3.8+ 已安装
- [ ] ✅ 项目已克隆到 `/opt/greed_bot`
- [ ] ✅ 虚拟环境已创建并激活
- [ ] ✅ 依赖包已安装
- [ ] ✅ 配置文件已创建 (`config_local.py`)

#### ⚙️ 配置检查
- [ ] ✅ `TELEGRAM_BOT_TOKEN` 已设置
- [ ] ✅ `DATABASE_URL` 已配置
- [ ] ✅ 时区设置正确
- [ ] ✅ 配置验证通过 (`python validate_config.py`)

#### 🚀 服务检查  
- [ ] ✅ Systemd服务已创建
- [ ] ✅ 服务已启用开机自启
- [ ] ✅ 服务运行正常
- [ ] ✅ 日志输出正常

#### 🔒 安全检查
- [ ] ✅ 文件权限设置正确
- [ ] ✅ 防火墙已配置
- [ ] ✅ 敏感文件已保护
- [ ] ✅ 日志轮转已设置

#### 🌐 网络检查
- [ ] ✅ Telegram API 连接正常
- [ ] ✅ CNN API 连接正常
- [ ] ✅ Bot响应用户消息
- [ ] ✅ 定时任务工作正常

---

## 📞 获取支持

### 🐛 问题报告
- **GitHub Issues**: [项目Issues页面](https://github.com/zijianwang90/greed_bot/issues)
- **电报群组**: [支持群组](https://t.me/greed_bot_support) (如果有)

### 📚 相关文档
- **项目主页**: [`README.md`](README.md) - 完整的项目介绍和使用说明
- **配置验证**: [`validate_config.py`](validate_config.py) - 配置文件验证工具
- **数据库迁移**: [`migrate_db.py`](migrate_db.py) - 数据库初始化和迁移

### 🔧 获取日志帮助
```bash
# 生成完整诊断报告
cd /opt/greed_bot
echo "=== 系统信息 ===" > debug_report.txt
uname -a >> debug_report.txt
python3 --version >> debug_report.txt
echo -e "\n=== 服务状态 ===" >> debug_report.txt
sudo systemctl status greed-bot >> debug_report.txt
echo -e "\n=== 最近错误 ===" >> debug_report.txt
sudo journalctl -u greed-bot --since "1 hour ago" | grep ERROR >> debug_report.txt
echo -e "\n=== 配置验证 ===" >> debug_report.txt
python validate_config.py >> debug_report.txt 2>&1

# 发送报告文件获取支持
echo "📋 诊断报告已生成: debug_report.txt"
```

---

**🎉 恭喜！您的CNN恐慌贪婪指数Bot已成功部署！**

记住：
1. ✅ **SQLite零配置** - 无需额外数据库服务
2. ✅ **Bot Token必填** - 从@BotFather获取
3. ✅ **Systemd自动化** - 服务自动重启和开机启动  
4. ✅ **定期维护** - 备份数据库，监控性能，更新代码

**Happy Bot Building! 🤖💼📈** 