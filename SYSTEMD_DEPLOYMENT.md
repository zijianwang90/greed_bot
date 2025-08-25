# Systemd 部署指南

本指南将帮助您在VPS上使用systemd后台运行Fear & Greed Index Bot。

## 前提条件

确保您已经：
- 将greed_bot目录复制到 `/opt/greed_bot`
- 安装了Python 3.8+
- 运行了安装脚本完成依赖安装
- 配置了 `config_local.py` 文件

## 步骤1: 准备启动脚本

将systemd启动脚本设置为可执行：

```bash
chmod +x /opt/greed_bot/systemd_start.sh
```

## 步骤2: 安装systemd服务

将service文件复制到systemd目录：

```bash
sudo cp /opt/greed_bot/greed-bot.service /etc/systemd/system/
```

重新加载systemd配置：

```bash
sudo systemctl daemon-reload
```

## 步骤3: 启动和管理服务

### 启动服务
```bash
sudo systemctl start greed-bot
```

### 开机自启动
```bash
sudo systemctl enable greed-bot
```

### 查看服务状态
```bash
sudo systemctl status greed-bot
```

### 重启服务
```bash
sudo systemctl restart greed-bot
```

### 停止服务
```bash
sudo systemctl stop greed-bot
```

### 禁用开机自启动
```bash
sudo systemctl disable greed-bot
```

## 步骤4: 查看日志

### 查看实时日志
```bash
sudo journalctl -u greed-bot -f
```

### 查看最近的日志
```bash
sudo journalctl -u greed-bot -n 50
```

### 查看今天的日志
```bash
sudo journalctl -u greed-bot --since today
```

### 查看指定时间范围的日志
```bash
sudo journalctl -u greed-bot --since "2024-01-01 00:00:00" --until "2024-01-01 23:59:59"
```

## 故障排除

### 1. 服务启动失败

检查服务状态：
```bash
sudo systemctl status greed-bot
```

查看详细错误信息：
```bash
sudo journalctl -u greed-bot -n 20
```

### 2. 常见问题

**权限问题**：
```bash
# 确保目录权限正确
sudo chown -R root:root /opt/greed_bot
sudo chmod +x /opt/greed_bot/systemd_start.sh
```

**虚拟环境问题**：
```bash
# 重新创建虚拟环境
cd /opt/greed_bot
sudo rm -rf venv
sudo ./install.sh
```

**配置文件问题**：
```bash
# 检查配置文件是否存在
ls -la /opt/greed_bot/config*.py
```

### 3. 性能监控

查看CPU和内存使用情况：
```bash
sudo systemctl show greed-bot --property=CPUUsageNSec,MemoryCurrent
```

## 完整的部署命令序列

以下是在VPS上完整部署的命令序列：

```bash
# 1. 进入项目目录
cd /opt/greed_bot

# 2. 设置脚本权限
chmod +x systemd_start.sh
chmod +x install.sh
chmod +x start_bot.sh

# 3. 安装systemd服务
sudo cp greed-bot.service /etc/systemd/system/

# 4. 重新加载systemd配置
sudo systemctl daemon-reload

# 5. 启动服务
sudo systemctl start greed-bot

# 6. 设置开机自启动
sudo systemctl enable greed-bot

# 7. 检查服务状态
sudo systemctl status greed-bot

# 8. 查看日志
sudo journalctl -u greed-bot -f
```

## 日志管理

### 限制日志大小

创建journald配置：
```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/greed-bot.conf > /dev/null << 'EOF'
[Journal]
SystemMaxUse=100M
SystemMaxFileSize=10M
SystemMaxFiles=10
EOF
```

重启journald服务：
```bash
sudo systemctl restart systemd-journald
```

### 日志轮转

系统会自动管理journal日志的轮转，您也可以手动清理：

```bash
# 清理超过7天的日志
sudo journalctl --vacuum-time=7d

# 清理超过100MB的日志
sudo journalctl --vacuum-size=100M

# 只保留最近10个日志文件
sudo journalctl --vacuum-files=10
```

## 安全注意事项

1. **用户权限**：服务当前以root用户运行。在生产环境中，建议创建专用用户：

```bash
# 创建专用用户
sudo useradd -r -s /bin/false greed-bot-user
sudo chown -R greed-bot-user:greed-bot-user /opt/greed_bot

# 修改service文件中的User和Group
User=greed-bot-user
Group=greed-bot-user
```

2. **文件权限**：确保配置文件包含敏感信息时权限设置正确：

```bash
sudo chmod 600 /opt/greed_bot/config_local.py
```

3. **防火墙**：如果bot需要访问外部API，确保防火墙配置正确。

## 监控和维护

### 设置邮件通知（可选）

如果希望在服务失败时收到邮件通知，可以配置systemd的邮件通知：

```bash
# 安装邮件工具
sudo apt-get install mailutils

# 在service文件中添加：
OnFailure=status-email-user@%i.service
```

### 定期检查

建议设置cron任务定期检查服务状态：

```bash
# 添加到crontab
*/5 * * * * systemctl is-active --quiet greed-bot || systemctl restart greed-bot
```

这样就完成了systemd的完整配置！您的bot将会稳定地在后台运行。
