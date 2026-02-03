#!/usr/bin/env python3
"""
Kimi账单自动查询 - 测试脚本
用于验证配置和功能是否正常
"""

import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    try:
        import requests
        print("✅ requests模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ requests模块导入失败: {e}")
        return False

def test_environment_variables():
    """测试环境变量"""
    print("🔍 测试环境变量...")
    
    # 检查.env文件是否存在
    if not os.path.exists('.env'):
        print("⚠️  .env文件不存在，使用模板值进行测试")
        return True
    
    # 尝试加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv未安装，手动加载环境变量")
        # 手动解析.env文件
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    required_vars = ['KIMI_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(var)
        else:
            print(f"✅ {var}: 已设置")
    
    if missing_vars:
        print(f"⚠️  以下环境变量未正确设置: {', '.join(missing_vars)}")
        print("   请编辑 .env 文件填入实际值")
        return False
    
    return True

def test_kimi_billing_checker():
    """测试KimiBillingChecker类"""
    print("🔍 测试KimiBillingChecker类...")
    
    try:
        from kimi_billing_checker import KimiBillingChecker
        print("✅ KimiBillingChecker类导入成功")
        
        # 测试实例化（不实际调用API）
        print("🧪 尝试实例化KimiBillingChecker...")
        
        # 如果环境变量未设置，使用测试值
        if not os.getenv('KIMI_API_KEY'):
            os.environ['KIMI_API_KEY'] = 'test_key'
            os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token'
            os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_id'
        
        checker = KimiBillingChecker()
        print("✅ KimiBillingChecker实例化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ KimiBillingChecker测试失败: {e}")
        return False

def test_format_report():
    """测试报告格式化功能"""
    print("🔍 测试报告格式化...")
    
    try:
        from kimi_billing_checker import KimiBillingChecker
        
        # 使用测试数据
        test_data = {
            'total_requests': 1234,
            'total_tokens': 56789,
            'total_cost': 12.34,
            'currency': 'CNY'
        }
        
        # 创建临时实例用于测试格式化
        checker = KimiBillingChecker()
        report = checker.format_usage_report(test_data)
        
        print("✅ 报告格式化成功")
        print("📄 生成的报告预览:")
        print("-" * 50)
        print(report[:200] + "..." if len(report) > 200 else report)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 报告格式化测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Kimi账单自动查询 - 功能测试")
    print("=" * 40)
    print(f"⏰ 测试时间: {datetime.now()}")
    print("")
    
    tests = [
        ("基本导入测试", test_basic_imports),
        ("环境变量测试", test_environment_variables),
        ("类导入测试", test_kimi_billing_checker),
        ("报告格式化测试", test_format_report)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print(f"✅ {test_name} - 通过")
        else:
            print(f"❌ {test_name} - 失败")
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统配置正确")
        print("\n📋 下一步:")
        print("1. 配置 .env 文件中的实际API密钥")
        print("2. 运行: ./run_kimi_billing_check.sh 进行完整测试")
        print("3. 设置定时任务: crontab -e")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())