# 🚀 快速设置指南

## 📋 新的配置文件结构

本项目使用**双配置文件结构**，分离个人设置和业务设置：

- **`config_local.py`** - 个人设置（不会被Git跟踪）
- **`config.py`** - 业务设置（会被Git跟踪）

## 🛠️ 快速设置步骤

### 1. 复制配置模板
```bash
cp config.example.py config.py
cp config_local.example.py config_local.py
```

### 2. 配置Bot Token（重要！）
编辑 `config_local.py`：
```python
# 必须配置：从 @BotFather 获取
TELEGRAM_BOT_TOKEN = "您的_BOT_TOKEN_这里"

# 可选配置
ADMIN_USER_ID = 123456789  # 您的Telegram用户ID
DATABASE_URL = "sqlite:///bot.db"  # 或PostgreSQL
DEFAULT_NOTIFICATION_TIME = "09:00"
DEFAULT_TIMEZONE = "Asia/Shanghai"
```

### 3. 验证配置
```bash
python validate_config.py
```

### 4. 启动Bot
```bash
./start_bot.sh
```

## 💡 为什么使用双配置文件？

### ✅ 优势
- **安全性**: 敏感信息（Token、密码）不会意外提交到Git
- **便捷性**: 更新代码时无需重新配置个人设置
- **团队协作**: 每个人有自己的`config_local.py`，共享业务配置
- **部署简单**: 只需复制一个`config_local.py`到新环境

### 📁 文件说明

| 文件 | 用途 | Git跟踪 | 内容 |
|------|------|---------|------|
| `config_local.py` | 个人设置 | ❌ 不跟踪 | Bot Token, 数据库, 个人偏好 |
| `config.py` | 业务设置 | ✅ 跟踪 | 功能开关, API设置, 限制参数 |
| `config_local.example.py` | 模板 | ✅ 跟踪 | 个人配置的示例 |
| `config.example.py` | 模板 | ✅ 跟踪 | 业务配置的示例 |

## 🔧 常见问题

### Q: 为什么Bot无法启动？
A: 检查以下几点：
1. 运行 `python validate_config.py` 验证配置
2. 确保 `TELEGRAM_BOT_TOKEN` 已正确设置
3. 检查 `config_local.py` 文件是否存在

### Q: 如何获取Telegram Bot Token？
A: 
1. 在Telegram中找到 @BotFather
2. 发送 `/newbot` 命令
3. 按提示设置Bot名称和用户名
4. 复制获得的Token到 `config_local.py`

### Q: 更新代码后需要重新配置吗？
A: **不需要！** 只要保留您的 `config_local.py` 文件，拉取最新代码后可直接使用。

### Q: 如何在生产环境部署？
A: 
1. 部署代码：`git clone` + 依赖安装
2. 复制配置：`cp your_backup/config_local.py ./`
3. 验证启动：`python validate_config.py && ./start_bot.sh`

## 🎯 快速命令参考

```bash
# 设置新环境
cp config_local.example.py config_local.py
nano config_local.py  # 编辑Token

# 验证配置
python validate_config.py

# 启动Bot
./start_bot.sh

# 检查状态（如果使用systemd）
sudo systemctl status greed-bot
```

---

**🎉 现在您可以享受更简洁的配置管理体验！** 