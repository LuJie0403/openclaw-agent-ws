#!/usr/bin/env python3
"""
Kimi API使用量本地记录系统
用于记录每次API调用的详细信息
"""

import json
import os
import datetime
from typing import Dict, List, Optional
import logging

class KimiUsageTracker:
    def __init__(self, data_dir: str = "usage_data"):
        self.data_dir = data_dir
        self.usage_file = os.path.join(data_dir, "usage_records.jsonl")
        self.monthly_summary_file = os.path.join(data_dir, "monthly_summary.json")
        
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/usage_tracker.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def record_api_call(self, request_data: Dict, response_data: Dict) -> bool:
        """记录一次API调用"""
        try:
            record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "request_id": response_data.get("id", ""),
                "model": request_data.get("model", ""),
                "input_tokens": self._count_tokens(request_data.get("messages", [])),
                "output_tokens": self._count_tokens(response_data.get("choices", [])),
                "total_tokens": response_data.get("usage", {}).get("total_tokens", 0),
                "cost": self._calculate_cost(
                    request_data.get("model", ""),
                    response_data.get("usage", {}).get("total_tokens", 0)
                ),
                "status": "success" if response_data.get("choices") else "failed",
                "response_time": response_data.get("response_time", 0)
            }
            
            # 追加写入JSONL文件
            with open(self.usage_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            self.logger.info(f"API调用已记录: {record['total_tokens']} tokens")
            return True
            
        except Exception as e:
            self.logger.error(f"记录API调用失败: {str(e)}")
            return False
    
    def _count_tokens(self, data) -> int:
        """估算token数量（简化版本）"""
        if isinstance(data, str):
            return len(data) // 4  # 粗略估算：4个字符≈1个token
        elif isinstance(data, list):
            return sum(len(str(item)) // 4 for item in data)
        else:
            return len(str(data)) // 4
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """计算调用成本（基于Kimi定价）"""
        # Kimi定价（需要根据实际情况调整）
        pricing = {
            "moonshot-v1-8k": {"input": 0.012, "output": 0.012},  # 每1K tokens的价格（CNY）
            "moonshot-v1-32k": {"input": 0.024, "output": 0.024},
            "moonshot-v1-128k": {"input": 0.06, "output": 0.06}
        }
        
        if model in pricing:
            # 假设输入输出各占一半（简化计算）
            cost_per_1k = (pricing[model]["input"] + pricing[model]["output"]) / 2
            return (tokens / 1000) * cost_per_1k
        else:
            return 0.0
    
    def get_monthly_stats(self, year_month: str = None) -> Dict:
        """获取月度统计数据"""
        if not year_month:
            year_month = datetime.datetime.now().strftime("%Y-%m")
        
        records = self._load_records_for_month(year_month)
        
        if not records:
            return {
                "year_month": year_month,
                "total_requests": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "success_rate": 0.0,
                "daily_average": 0,
                "peak_day": None,
                "model_usage": {},
                "daily_breakdown": []
            }
        
        # 计算统计数据
        total_requests = len(records)
        total_tokens = sum(r.get("total_tokens", 0) for r in records)
        total_cost = sum(r.get("cost", 0.0) for r in records)
        successful_requests = len([r for r in records if r.get("status") == "success"])
        
        # 模型使用统计
        model_usage = {}
        daily_stats = {}
        
        for record in records:
            model = record.get("model", "unknown")
            model_usage[model] = model_usage.get(model, 0) + 1
            
            # 按天统计
            date = record["timestamp"][:10]  # YYYY-MM-DD
            if date not in daily_stats:
                daily_stats[date] = {"requests": 0, "tokens": 0, "cost": 0.0}
            daily_stats[date]["requests"] += 1
            daily_stats[date]["tokens"] += record.get("total_tokens", 0)
            daily_stats[date]["cost"] += record.get("cost", 0.0)
        
        # 找出峰值日期
        peak_day = max(daily_stats.items(), key=lambda x: x[1]["requests"])[0] if daily_stats else None
        
        # 计算日均使用量
        days_in_month = len(daily_stats) or 1
        daily_average = total_requests / days_in_month
        
        return {
            "year_month": year_month,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 2),
            "success_rate": round((successful_requests / total_requests) * 100, 1) if total_requests > 0 else 0.0,
            "daily_average": round(daily_average, 1),
            "peak_day": peak_day,
            "model_usage": model_usage,
            "daily_breakdown": [
                {"date": date, **stats} 
                for date, stats in sorted(daily_stats.items())
            ]
        }
    
    def _load_records_for_month(self, year_month: str) -> List[Dict]:
        """加载指定月份的所有记录"""
        records = []
        
        if not os.path.exists(self.usage_file):
            return records
        
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        record = json.loads(line)
                        if record["timestamp"].startswith(year_month):
                            records.append(record)
        except Exception as e:
            self.logger.error(f"加载记录失败: {str(e)}")
        
        return records
    
    def save_monthly_summary(self, year_month: str = None) -> bool:
        """保存月度摘要"""
        if not year_month:
            year_month = datetime.datetime.now().strftime("%Y-%m")
        
        stats = self.get_monthly_stats(year_month)
        
        try:
            # 加载现有摘要
            summaries = {}
            if os.path.exists(self.monthly_summary_file):
                with open(self.monthly_summary_file, 'r', encoding='utf-8') as f:
                    summaries = json.load(f)
            
            # 更新当前月份数据
            summaries[year_month] = stats
            
            # 保存回文件
            with open(self.monthly_summary_file, 'w', encoding='utf-8') as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"月度摘要已保存: {year_month}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存月度摘要失败: {str(e)}")
            return False
    
    def get_usage_trend(self, months: int = 3) -> List[Dict]:
        """获取使用趋势"""
        trends = []
        current_date = datetime.datetime.now()
        
        for i in range(months):
            # 计算月份
            if current_date.month - i <= 0:
                year = current_date.year - 1
                month = current_date.month - i + 12
            else:
                year = current_date.year
                month = current_date.month - i
            
            year_month = f"{year}-{month:02d}"
            stats = self.get_monthly_stats(year_month)
            
            if stats["total_requests"] > 0:  # 只包含有数据的月份
                trends.append({
                    "year_month": year_month,
                    "total_requests": stats["total_requests"],
                    "total_tokens": stats["total_tokens"],
                    "total_cost": stats["total_cost"],
                    "daily_average": stats["daily_average"]
                })
        
        return list(reversed(trends))  # 按时间顺序排列

# 使用示例
if __name__ == "__main__":
    tracker = KimiUsageTracker()
    
    # 模拟一些API调用记录
    test_requests = [
        {
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": "你好，请介绍一下Kimi"}]
        },
        {
            "model": "moonshot-v1-8k", 
            "messages": [{"role": "user", "content": "写一段关于人工智能的介绍"}]
        }
    ]
    
    test_responses = [
        {
            "id": "chat-001",
            "choices": [{"message": {"content": "你好！我是Kimi..."}}],
            "usage": {"total_tokens": 150},
            "response_time": 1.2
        },
        {
            "id": "chat-002", 
            "choices": [{"message": {"content": "人工智能是..."}}],
            "usage": {"total_tokens": 280},
            "response_time": 1.5
        }
    ]
    
    # 记录测试数据
    for req, resp in zip(test_requests, test_responses):
        tracker.record_api_call(req, resp)
    
    # 获取月度统计
    current_month = datetime.datetime.now().strftime("%Y-%m")
    stats = tracker.get_monthly_stats(current_month)
    print(f"本月统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    # 保存月度摘要
    tracker.save_monthly_summary(current_month)