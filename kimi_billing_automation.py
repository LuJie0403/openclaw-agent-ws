#!/usr/bin/env python3
"""
Kimi API月度账单自动发送系统
整合使用量追踪、报告生成和消息发送
"""

import os
import sys
import datetime
import logging
import json
from typing import Optional

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kimi_usage_tracker import KimiUsageTracker
from kimi_report_generator import KimiReportGenerator

class KimiBillingAutomation:
    def __init__(self):
        # 配置日志
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.tracker = KimiUsageTracker()
        self.report_generator = KimiReportGenerator()
        
        # 获取配置
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # 可选配置
        self.auto_backup = os.getenv('AUTO_BACKUP', 'true').lower() == 'true'
        self.report_format = os.getenv('REPORT_FORMAT', 'detailed')  # detailed, simple
        self.send_time = os.getenv('SEND_TIME', '09:00')  # 发送时间
        
    def setup_logging(self):
        """设置日志系统"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = datetime.datetime.now().strftime("kimi_billing_%Y%m.log")
        log_path = os.path.join(log_dir, log_filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def check_configuration(self) -> bool:
        """检查必要的配置"""
        required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith('your_'):
                missing_vars.append(var)
        
        if missing_vars:
            self.logger.error(f"缺少必要配置: {', '.join(missing_vars)}")
            return False
        
        self.logger.info("✅ 配置检查通过")
        return True
    
    def generate_monthly_billing(self, year_month: str = None) -> Optional[Dict]:
        """生成月度账单"""
        try:
            if not year_month:
                year_month = datetime.datetime.now().strftime("%Y-%m")
            
            self.logger.info(f"开始生成 {year_month} 月度账单...")
            
            # 1. 确保月度数据已保存
            self.logger.info("保存月度摘要...")
            self.tracker.save_monthly_summary(year_month)
            
            # 2. 生成详细报告
            self.logger.info("生成详细报告...")
            report = self.report_generator.generate_monthly_report(year_month)
            
            # 3. 生成Telegram消息
            self.logger.info("生成Telegram消息...")
            telegram_message = self.report_generator.format_telegram_report(report)
            
            billing_data = {
                "year_month": year_month,
                "report": report,
                "telegram_message": telegram_message,
                "generated_at": datetime.datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ 月度账单生成完成: {year_month}")
            return billing_data
            
        except Exception as e:
            self.logger.error(f"生成月度账单失败: {str(e)}")
            return None
    
    def send_telegram_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """发送Telegram消息"""
        try:
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_notification': False
            }
            
            # 如果消息太长，进行分割
            if len(message) > 4096:  # Telegram消息长度限制
                self.logger.warning("消息过长，进行分割发送")
                return self._send_long_message(message, parse_mode)
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("✅ Telegram消息发送成功")
                return True
            else:
                self.logger.error(f"❌ Telegram消息发送失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送Telegram消息时出错: {str(e)}")
            return False
    
    def _send_long_message(self, message: str, parse_mode: str) -> bool:
        """发送长消息（分割发送）"""
        try:
            # 按段落分割消息
            paragraphs = message.split('\n\n')
            current_message = ""
            messages_sent = 0
            
            for paragraph in paragraphs:
                # 检查添加新段落后是否超出限制
                test_message = current_message + ("\n\n" if current_message else "") + paragraph
                
                if len(test_message) > 3800:  # 留一些余量
                    # 发送当前消息
                    if current_message:
                        if self.send_telegram_message(current_message, parse_mode):
                            messages_sent += 1
                        current_message = ""
                
                current_message = paragraph if not current_message else current_message + "\n\n" + paragraph
            
            # 发送最后一条消息
            if current_message:
                if self.send_telegram_message(current_message, parse_mode):
                    messages_sent += 1
            
            self.logger.info(f"长消息分割发送完成: {messages_sent} 条消息")
            return messages_sent > 0
            
        except Exception as e:
            self.logger.error(f"分割发送长消息失败: {str(e)}")
            return False
    
    def backup_data(self, year_month: str = None) -> bool:
        """备份数据"""
        try:
            if not year_month:
                year_month = datetime.datetime.now().strftime("%Y-%m")
            
            self.logger.info("开始数据备份...")
            
            # 创建备份目录
            backup_dir = f"backups/{year_month}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份使用记录
            import shutil
            
            # 备份主要数据文件
            data_files = [
                ("usage_data/usage_records.jsonl", "usage_records.jsonl"),
                ("usage_data/monthly_summary.json", "monthly_summary.json"),
                (f"reports/kimi_usage_report_{year_month}.json", f"report_{year_month}.json")
            ]
            
            for src_file, dest_name in data_files:
                if os.path.exists(src_file):
                    dest_path = os.path.join(backup_dir, dest_name)
                    shutil.copy2(src_file, dest_path)
                    self.logger.info(f"已备份: {dest_name}")
            
            self.logger.info(f"✅ 数据备份完成: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据备份失败: {str(e)}")
            return False
    
    def run_monthly_billing(self, year_month: str = None, force_send: bool = False) -> bool:
        """运行完整的月度账单流程"""
        try:
            self.logger.info("🚀 开始执行月度账单流程...")
            
            # 1. 检查配置
            if not self.check_configuration():
                return False
            
            # 2. 生成账单
            billing_data = self.generate_monthly_billing(year_month)
            if not billing_data:
                self.logger.error("月度账单生成失败")
                return False
            
            # 3. 发送报告
            message = billing_data["telegram_message"]
            if self.send_telegram_message(message):
                self.logger.info("✅ 月度报告发送成功")
            else:
                self.logger.error("❌ 月度报告发送失败")
                return False
            
            # 4. 数据备份（如果启用）
            if self.auto_backup:
                self.backup_data(billing_data["year_month"])
            
            self.logger.info("🎉 月度账单流程执行完成")
            return True
            
        except Exception as e:
            self.logger.error(f"月度账单流程执行失败: {str(e)}")
            
            # 发送错误通知
            error_message = f"""❌ **Kimi月度账单生成失败**

错误时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
错误信息: {str(e)}

请检查系统日志获取详细信息。
"""
            self.send_telegram_message(error_message)
            return False
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        try:
            # 检查数据文件
            usage_file = "usage_data/usage_records.jsonl"
            summary_file = "usage_data/monthly_summary.json"
            
            status = {
                "system_time": datetime.datetime.now().isoformat(),
                "configuration_status": {
                    "telegram_configured": bool(self.telegram_bot_token and self.telegram_chat_id),
                    "auto_backup_enabled": self.auto_backup,
                    "report_format": self.report_format
                },
                "data_files_status": {
                    "usage_records_exists": os.path.exists(usage_file),
                    "monthly_summary_exists": os.path.exists(summary_file)
                },
                "current_month_usage": self.tracker.get_monthly_stats(),
                "recent_logs": self._get_recent_logs()
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"获取系统状态失败: {str(e)}")
            return {"error": str(e)}
    
    def _get_recent_logs(self, lines: int = 10) -> List[str]:
        """获取最近的日志"""
        try:
            log_file = f"logs/kimi_billing_{datetime.datetime.now().strftime('%Y%m')}.log"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    return [line.strip() for line in all_lines[-lines:]]
            return []
        except Exception:
            return []

def main():
    """主函数"""
    automation = KimiBillingAutomation()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser(description='Kimi API月度账单自动发送系统')
    parser.add_argument('--month', type=str, help='指定月份 (YYYY-MM格式)', default=None)
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('--test-message', action='store_true', help='测试消息发送')
    parser.add_argument('--force', action='store_true', help='强制发送报告')
    
    args = parser.parse_args()
    
    try:
        if args.status:
            # 显示系统状态
            status = automation.get_system_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
            return 0
        
        elif args.test_message:
            # 测试消息发送
            test_message = """🧪 **Kimi账单系统测试消息**

这是一条测试消息，用于验证Telegram消息发送功能是否正常。

⏰ 测试时间: """ + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if automation.send_telegram_message(test_message):
                print("✅ 测试消息发送成功")
                return 0
            else:
                print("❌ 测试消息发送失败")
                return 1
        
        else:
            # 运行月度账单流程
            success = automation.run_monthly_billing(args.month, args.force)
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断执行")
        return 1
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())