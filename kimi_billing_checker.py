#!/usr/bin/env python3
"""
Kimi API使用量自动查询脚本
任务名称：Kimi账单自动查询
功能：每月3号自动查询Kimi API使用量并通过Telegram发送报告给路杰
"""

import requests
import json
import datetime
import os
from typing import Dict, Optional

class KimiBillingChecker:
    def __init__(self):
        # Kimi API配置 - 需要从环境变量获取
        self.kimi_api_key = os.getenv('KIMI_API_KEY')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not all([self.kimi_api_key, self.telegram_bot_token, self.telegram_chat_id]):
            raise ValueError("缺少必要的环境变量配置")
    
    def get_current_month_usage(self) -> Optional[Dict]:
        """获取本月API使用量数据"""
        try:
            # 获取当前月份
            now = datetime.datetime.now()
            current_month = now.strftime('%Y-%m')
            
            # 构建API请求
            headers = {
                'Authorization': f'Bearer {self.kimi_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 调用Kimi API获取使用量数据
            # 注意：这里需要根据Kimi API的实际endpoint进行调整
            api_url = 'https://api.moonshot.cn/v1/usage'
            
            params = {
                'month': current_month,
                'include_details': True
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"获取API使用量时出错: {str(e)}")
            return None
    
    def format_usage_report(self, usage_data: Dict) -> str:
        """格式化使用量报告"""
        if not usage_data:
            return "❌ 无法获取Kimi API使用量数据"
        
        current_month = datetime.datetime.now().strftime('%Y年%m月')
        
        # 提取关键数据
        total_requests = usage_data.get('total_requests', 0)
        total_tokens = usage_data.get('total_tokens', 0)
        cost_amount = usage_data.get('total_cost', 0)
        currency = usage_data.get('currency', 'CNY')
        
        # 计算日均使用量
        current_day = datetime.datetime.now().day
        avg_daily_requests = total_requests / current_day if current_day > 0 else 0
        avg_daily_tokens = total_tokens / current_day if current_day > 0 else 0
        
        # 构建报告消息
        report = f"""📊 **Kimi API {current_month}使用报告**

🔢 **基本统计**
• 总请求次数: {total_requests:,}
• 总Token消耗: {total_tokens:,}
• 预估费用: {cost_amount:.2f} {currency}

📈 **日均使用**
• 日均请求: {avg_daily_requests:.0f} 次
• 日均Token: {avg_daily_tokens:,.0f}

💡 **使用建议**
• 监控使用量趋势，合理规划API调用
• 如需更高额度，请联系服务提供商

📅 **报告生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return report
    
    def send_telegram_message(self, message: str) -> bool:
        """通过Telegram发送消息"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_notification': False
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print("✅ Telegram消息发送成功")
                return True
            else:
                print(f"❌ Telegram消息发送失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"发送Telegram消息时出错: {str(e)}")
            return False
    
    def run_monthly_check(self) -> bool:
        """执行月度检查任务"""
        print(f"开始执行Kimi API月度检查任务 - {datetime.datetime.now()}")
        
        try:
            # 1. 查询API使用量
            print("正在查询Kimi API使用量...")
            usage_data = self.get_current_month_usage()
            
            # 2. 统计本月使用数据并生成报告
            print("正在生成使用报告...")
            report = self.format_usage_report(usage_data)
            
            # 3. 通过Telegram发送报告
            print("正在发送Telegram消息...")
            success = self.send_telegram_message(report)
            
            if success:
                print("✅ Kimi API月度检查任务完成")
            else:
                print("❌ Kimi API月度检查任务失败")
            
            return success
            
        except Exception as e:
            print(f"执行月度检查任务时出错: {str(e)}")
            
            # 发送错误通知
            error_message = f"""❌ **Kimi API月度检查失败**

错误信息: {str(e)}

请检查系统配置和API连接状态。
            """
            self.send_telegram_message(error_message)
            return False

def main():
    """主函数"""
    print("🚀 启动Kimi账单自动查询任务")
    
    try:
        checker = KimiBillingChecker()
        success = checker.run_monthly_check()
        
        if success:
            print("🎉 任务执行成功")
            exit(0)
        else:
            print("💥 任务执行失败")
            exit(1)
            
    except ValueError as e:
        print(f"配置错误: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"未预期的错误: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()