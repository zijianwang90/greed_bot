#!/usr/bin/env python3
"""
配置验证脚本
检查 config.py 和 config_local.py 配置是否正确
"""

import os
import sys
from pathlib import Path

def check_file_exists(filename):
    """检查文件是否存在"""
    if not Path(filename).exists():
        print(f"❌ {filename} 文件不存在")
        return False
    print(f"✅ {filename} 文件存在")
    return True

def validate_config():
    """验证配置"""
    print("🔍 开始验证配置文件...")
    print("=" * 50)
    
    # 检查配置文件是否存在
    config_exists = check_file_exists("config.py")
    config_local_exists = check_file_exists("config_local.py")
    
    if not config_local_exists:
        print("\n💡 请运行: cp config_local.example.py config_local.py")
        print("💡 然后编辑 config_local.py 添加您的 Bot Token")
        
    if not config_exists:
        print("\n⚠️  config.py 缺失，但这是正常的，因为它会从 config_local.py 导入设置")
    
    if not config_local_exists:
        return False
    
    print("\n🔍 检查配置项...")
    
    try:
        # 尝试导入配置
        import config
        
        # 检查必需的配置项
        required_configs = [
            ('TELEGRAM_BOT_TOKEN', 'Telegram Bot Token'),
            ('DATABASE_URL', '数据库URL'),
            ('CNN_FEAR_GREED_API', 'CNN恐慌贪婪指数API'),
        ]
        
        missing_configs = []
        invalid_configs = []
        
        for config_name, description in required_configs:
            if hasattr(config, config_name):
                value = getattr(config, config_name)
                if value and value != "YOUR_BOT_TOKEN_HERE":
                    print(f"✅ {description} 已配置")
                else:
                    print(f"❌ {description} 未配置或为默认值")
                    invalid_configs.append((config_name, description))
            else:
                print(f"❌ {description} 缺失")
                missing_configs.append((config_name, description))
        
        # 检查可选配置
        optional_configs = [
            ('ADMIN_USER_ID', '管理员用户ID'),
            ('BOT_USERNAME', 'Bot用户名'),
            ('DEFAULT_LANGUAGE', '默认语言'),
        ]
        
        print("\n🔍 检查可选配置...")
        for config_name, description in optional_configs:
            if hasattr(config, config_name):
                value = getattr(config, config_name)
                if value:
                    print(f"✅ {description}: {value}")
                else:
                    print(f"⚠️  {description} 未设置（使用默认值）")
            else:
                print(f"⚠️  {description} 缺失（使用默认值）")
        
        # 总结
        print("\n" + "=" * 50)
        if missing_configs or invalid_configs:
            print("❌ 配置验证失败!")
            
            if missing_configs:
                print("\n缺失的配置项:")
                for config_name, description in missing_configs:
                    print(f"  - {config_name}: {description}")
            
            if invalid_configs:
                print("\n需要配置的项目:")
                for config_name, description in invalid_configs:
                    if config_name == 'TELEGRAM_BOT_TOKEN':
                        print(f"  - {config_name}: 请在 config_local.py 中设置您的 Bot Token")
                    else:
                        print(f"  - {config_name}: {description}")
            
            print(f"\n💡 请编辑 config_local.py 文件配置必需的设置")
            return False
        else:
            print("✅ 配置验证通过!")
            print("\n🚀 您可以运行 './start_bot.sh' 或 'python main.py' 启动Bot")
            return True
            
    except ImportError as e:
        print(f"❌ 导入配置失败: {e}")
        print("\n可能的原因:")
        print("1. config_local.py 中有语法错误")
        print("2. 缺少必需的配置项")
        print("3. 配置文件格式不正确")
        return False
    
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    if validate_config():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 