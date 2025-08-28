#!/usr/bin/env python3
"""
VIX命令诊断脚本
检查VIX功能的相关配置和依赖
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查必要的依赖包"""
    print("🔍 检查依赖包...")

    required_packages = [
        'telegram',
        'aiohttp',
        'sqlalchemy',
        'pandas',
        'python-dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ 所有依赖包已安装")
        return True

def check_config():
    """检查配置文件"""
    print("\n🔍 检查配置文件...")

    try:
        import config
        print("✅ config.py 导入成功")

        # 检查关键配置
        if hasattr(config, 'TELEGRAM_BOT_TOKEN'):
            if config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
                print("✅ TELEGRAM_BOT_TOKEN 已配置")
            else:
                print("❌ TELEGRAM_BOT_TOKEN 未配置")
                return False
        else:
            print("❌ TELEGRAM_BOT_TOKEN 未找到")
            return False

        print(f"✅ LOG_LEVEL: {getattr(config, 'LOG_LEVEL', 'INFO')}")
        print(f"✅ ENABLE_VIX_DATA: {getattr(config, 'ENABLE_VIX_DATA', True)}")

        return True

    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def check_handlers():
    """检查命令处理器"""
    print("\n🔍 检查命令处理器...")

    try:
        from bot.handlers import vix_handler, vix_history_handler
        print("✅ vix_handler 导入成功")
        print("✅ vix_history_handler 导入成功")
        return True
    except ImportError as e:
        print(f"❌ 处理器导入失败: {e}")
        return False

def check_main_registration():
    """检查主程序中的命令注册"""
    print("\n🔍 检查主程序命令注册...")

    try:
        # 读取 main.py 文件内容
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否包含 VIX 命令注册
        checks = [
            'vix_handler',
            'CommandHandler("vix", vix_handler)',
            'CommandHandler("vix_history", vix_history_handler)'
        ]

        for check in checks:
            if check in content:
                print(f"✅ {check}")
            else:
                print(f"❌ 缺失: {check}")
                return False

        return True

    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def test_vix_fetcher():
    """测试VIX数据获取器"""
    print("\n🔍 测试VIX数据获取器...")

    try:
        from data.fetcher import FearGreedDataFetcher
        print("✅ FearGreedDataFetcher 导入成功")

        # 检查是否有 get_vix_data 方法
        if hasattr(FearGreedDataFetcher, 'get_vix_data'):
            print("✅ get_vix_data 方法存在")
            return True
        else:
            print("❌ get_vix_data 方法不存在")
            return False

    except Exception as e:
        print(f"❌ 数据获取器测试失败: {e}")
        return False

def test_utils_functions():
    """测试工具函数"""
    print("\n🔍 测试工具函数...")

    try:
        from bot.utils import format_vix_message, get_vix_emoji, get_vix_level_interpretation
        print("✅ VIX工具函数导入成功")

        # 测试表情符号函数
        test_value = 18.5
        emoji = get_vix_emoji(test_value)
        print(f"✅ 表情符号测试: VIX {test_value} -> {emoji}")

        # 测试解读函数
        interpretation = get_vix_level_interpretation(test_value, "zh")
        print(f"✅ 解读测试: {interpretation}")

        return True

    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False

def main():
    """主诊断函数"""
    print("🚀 VIX功能诊断工具")
    print("=" * 50)

    all_checks = [
        check_dependencies,
        check_config,
        check_handlers,
        check_main_registration,
        test_vix_fetcher,
        test_utils_functions
    ]

    passed = 0
    total = len(all_checks)

    for check in all_checks:
        if check():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 诊断结果: {passed}/{total} 项通过")

    if passed == total:
        print("✅ VIX功能配置正确！")
        print("\n💡 建议:")
        print("1. 启动机器人: python3 main.py")
        print("2. 在Telegram中发送 /vix 命令")
        print("3. 检查控制台日志输出")
    else:
        print("❌ 发现配置问题，请修复上述问题后再试")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
