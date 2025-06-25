# 🚀 VPS部署完整指南

## 📋 部署前准备

### 系统要求
- Ubuntu 18.04+ / CentOS 7+ / Debian 9+
- Python 3.8+
- 至少512MB内存
- 1GB磁盘空间

### 1. 更新系统并安装依赖

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git screen

# CentOS/RHEL
sudo yum update
sudo yum install -y python3 python3-pip git screen
```

## 📦 部署步骤

### 1. 克隆项目
```bash
cd /opt
sudo git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot
sudo chown -R $USER:$USER /opt/greed_bot
```

### 2. 运行安装脚本
```bash
chmod +x install.sh
./install.sh
```

### 3. 配置Bot

#### 创建配置文件
```bash
cp config.example.py config.py
nano config.py
```

#### 配置示例（重要部分）
```python
# Telegram Bot Token (必填)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# SQLite数据库路径（推荐使用绝对路径）
DATABASE_URL = "sqlite:///opt/greed_bot/bot.db"

# 或者使用相对路径（在项目目录下）
# DATABASE_URL = "sqlite:///bot.db"

# 默认通知时间
DEFAULT_NOTIFICATION_TIME = "09:00"

# 时区设置
DEFAULT_TIMEZONE = "Asia/Shanghai"  # 根据需要调整

# 日志设置
LOG_LEVEL = "INFO"
LOG_FILE = "/opt/greed_bot/bot.log"
```

## 💾 SQLite数据库说明

**重要：SQLite不需要启动服务！**

SQLite是文件数据库，当Bot运行时会自动：
1. 创建数据库文件（如果不存在）
2. 创建必要的数据表
3. 处理所有数据库操作

### 数据库文件位置
- 默认：项目目录下的 `bot.db`
- 推荐：使用绝对路径 `/opt/greed_bot/bot.db`

### 数据库权限
```bash
# 确保Bot有权限读写数据库文件和目录
chmod 755 /opt/greed_bot
chmod 644 /opt/greed_bot/bot.db  # 如果文件已存在
```

## 🚀 启动Bot

### 方法1：直接启动（测试用）
```bash
cd /opt/greed_bot
source venv/bin/activate
python main.py
```

### 方法2：使用Screen（后台运行）
```bash
cd /opt/greed_bot
screen -S greed_bot
source venv/bin/activate
python main.py

# 按 Ctrl + A, 然后按 D 退出screen
# 重新进入: screen -r greed_bot
```

### 方法3：使用systemd服务（推荐）

#### 创建服务文件
```bash
sudo nano /etc/systemd/system/greed-bot.service
```

#### 服务配置内容
```ini
[Unit]
Description=CNN Fear & Greed Index Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/greed_bot
Environment=PATH=/opt/greed_bot/venv/bin
ExecStart=/opt/greed_bot/venv/bin/python /opt/greed_bot/main.py
Restart=always
RestartSec=10

# 日志设置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=greed-bot

[Install]
WantedBy=multi-user.target
```

#### 启动服务
```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable greed-bot

# 启动服务
sudo systemctl start greed-bot

# 查看状态
sudo systemctl status greed-bot

# 查看日志
sudo journalctl -u greed-bot -f
```

## 📊 监控和维护

### 查看Bot状态
```bash
# 检查进程
ps aux | grep python | grep main.py

# 检查服务状态
sudo systemctl status greed-bot

# 查看实时日志
sudo journalctl -u greed-bot -f
```

### 数据库维护
```bash
# 查看数据库文件大小
ls -lh /opt/greed_bot/bot.db

# 备份数据库
cp /opt/greed_bot/bot.db /opt/greed_bot/bot.db.backup.$(date +%Y%m%d)

# 检查数据库完整性（如果安装了sqlite3）
sqlite3 /opt/greed_bot/bot.db "PRAGMA integrity_check;"
```

### 更新Bot
```bash
cd /opt/greed_bot
git pull origin main
sudo systemctl restart greed-bot
```

## 🔧 故障排除

### 常见问题

#### 1. Bot无法启动
```bash
# 检查配置文件
python -c "import config; print('Config OK')"

# 检查Python环境
source venv/bin/activate
python --version
pip list
```

#### 2. 数据库权限问题
```bash
# 检查文件权限
ls -la /opt/greed_bot/bot.db

# 修复权限
sudo chown $USER:$USER /opt/greed_bot/bot.db
chmod 644 /opt/greed_bot/bot.db
```

#### 3. 网络连接问题
```bash
# 测试网络连接
curl -I https://api.telegram.org
curl -I https://production.dataviz.cnn.io/index/fearandgreed/graphdata
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head
```

### 日志分析
```bash
# 查看错误日志
sudo journalctl -u greed-bot --since "1 hour ago" | grep ERROR

# 查看Bot日志文件
tail -f /opt/greed_bot/bot.log

# 按日期查看日志
sudo journalctl -u greed-bot --since "2024-01-15"
```

## 🔒 安全设置

### 防火墙配置
```bash
# Ubuntu/Debian (UFW)
sudo ufw allow ssh
sudo ufw allow 443/tcp  # 如果使用webhook
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=443/tcp  # 如果使用webhook
sudo firewall-cmd --reload
```

### 文件权限
```bash
# 设置安全的文件权限
chmod 600 /opt/greed_bot/config.py  # 配置文件仅所有者可读写
chmod 644 /opt/greed_bot/bot.db     # 数据库文件
chmod -R 755 /opt/greed_bot/        # 项目目录
```

## 📈 性能优化

### 系统级优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
```

### Python优化
在 `config.py` 中调整：
```python
# 减少数据更新频率（如果用户不多）
DATA_UPDATE_INTERVAL = 120  # 2小时更新一次

# 限制最大用户数
MAX_USERS = 1000

# 启用缓存
ENABLE_CACHING = True
CACHE_TTL = 600  # 10分钟缓存
```

## 🏃‍♂️ 快速启动命令

```bash
# 一键部署脚本
cat > /tmp/deploy.sh << 'EOF'
#!/bin/bash
cd /opt
sudo git clone https://github.com/zijianwang90/greed_bot.git
cd greed_bot
sudo chown -R $USER:$USER /opt/greed_bot
chmod +x install.sh
./install.sh
echo "请编辑 config.py 文件添加您的Bot Token"
echo "然后运行: sudo systemctl start greed-bot"
EOF

chmod +x /tmp/deploy.sh
/tmp/deploy.sh
```

---

**部署完成！** 🎉

记住：
1. ✅ SQLite不需要启动服务
2. ✅ 配置文件中设置正确的Bot Token
3. ✅ 使用systemd服务确保稳定运行
4. ✅ 定期备份数据库文件 