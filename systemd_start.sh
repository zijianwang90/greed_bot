#!/bin/bash

# Systemd启动脚本 - Fear & Greed Index Bot
# 此脚本专门用于systemd服务启动，确保正确的环境配置

# 设置工作目录
cd /opt/greed_bot

# 检查虚拟环境是否存在
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "错误: 虚拟环境不存在，请先运行安装脚本"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.py" ] || [ ! -f "config_local.py" ]; then
    echo "错误: 配置文件不存在，请检查config.py和config_local.py"
    exit 1
fi

# 激活虚拟环境并启动bot
source venv/bin/activate

# 检查Python和依赖
if ! python -c "import telegram" 2>/dev/null; then
    echo "错误: 依赖包未正确安装"
    exit 1
fi

# 启动应用
exec python main.py
