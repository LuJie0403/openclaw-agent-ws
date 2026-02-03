#!/usr/bin/env python3
"""
Kimi API月度报告生成器
生成详细的使用报告和分析
"""

import json
import os
import datetime
from typing import Dict, List
from kimi_usage_tracker import KimiUsageTracker

class KimiReportGenerator:
    def __init__(self):
        self.tracker = KimiUsageTracker()
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_monthly_report(self, year_month: str = None) -> Dict:
        """生成月度报告"""
        if not year_month:
            year_month = datetime.datetime.now().strftime("%Y-%m")
        
        # 获取月度统计数据
        monthly_stats = self.tracker.get_monthly_stats(year_month)
        usage_trend = self.tracker.get_usage_trend(3)  # 最近3个月趋势
        
        # 生成详细报告
        report = {
            "report_info": {
                "generated_at": datetime.datetime.now().isoformat(),
                "report_period": year_month,
                "report_type": "monthly_usage_report"
            },
            "usage_summary": {
                "total_requests": monthly_stats["total_requests"],
                "total_tokens": monthly_stats["total_tokens"],
                "total_cost": monthly_stats["total_cost"],
                "success_rate": monthly_stats["success_rate"],
                "daily_average": monthly_stats["daily_average"],
                "peak_usage_day": monthly_stats["peak_day"]
            },
            "model_breakdown": self._generate_model_breakdown(monthly_stats["model_usage"]),
            "daily_analysis": self._generate_daily_analysis(monthly_stats["daily_breakdown"]),
            "trend_analysis": self._generate_trend_analysis(usage_trend),
            "cost_analysis": self._generate_cost_analysis(monthly_stats, usage_trend),
            "recommendations": self._generate_recommendations(monthly_stats, usage_trend)
        }
        
        # 保存报告
        self._save_report(report, year_month)
        
        return report
    
    def _generate_model_breakdown(self, model_usage: Dict) -> Dict:
        """生成模型使用情况分析"""
        total_requests = sum(model_usage.values())
        
        breakdown = {}
        for model, count in model_usage.items():
            percentage = (count / total_requests * 100) if total_requests > 0 else 0
            breakdown[model] = {
                "requests": count,
                "percentage": round(percentage, 1)
            }
        
        return {
            "total_models": len(model_usage),
            "most_used_model": max(model_usage.items(), key=lambda x: x[1])[0] if model_usage else None,
            "model_distribution": breakdown
        }
    
    def _generate_daily_analysis(self, daily_breakdown: List) -> Dict:
        """生成日使用量分析"""
        if not daily_breakdown:
            return {"analysis_available": False}
        
        requests_list = [day["requests"] for day in daily_breakdown]
        tokens_list = [day["tokens"] for day in daily_breakdown]
        costs_list = [day["cost"] for day in daily_breakdown]
        
        return {
            "analysis_available": True,
            "total_days": len(daily_breakdown),
            "busiest_day": max(daily_breakdown, key=lambda x: x["requests"])["date"],
            "quietest_day": min(daily_breakdown, key=lambda x: x["requests"])["date"],
            "average_per_day": {
                "requests": round(sum(requests_list) / len(requests_list), 1),
                "tokens": round(sum(tokens_list) / len(tokens_list)),
                "cost": round(sum(costs_list) / len(costs_list), 2)
            },
            "usage_consistency": self._calculate_consistency(requests_list)
        }
    
    def _calculate_consistency(self, values: List) -> str:
        """计算使用一致性"""
        if len(values) < 2:
            return "数据不足"
        
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # 计算变异系数
        cv = (std_dev / avg) * 100 if avg > 0 else 0
        
        if cv < 20:
            return "非常稳定"
        elif cv < 40:
            return "相对稳定"
        elif cv < 60:
            return "中等波动"
        else:
            return "波动较大"
    
    def _generate_trend_analysis(self, usage_trend: List) -> Dict:
        """生成趋势分析"""
        if len(usage_trend) < 2:
            return {"analysis_available": False}
        
        # 计算环比变化
        latest = usage_trend[-1]
        previous = usage_trend[-2] if len(usage_trend) >= 2 else None
        
        trend_data = {
            "analysis_available": True,
            "months_analyzed": len(usage_trend),
            "trend_period": f"{usage_trend[0]['year_month']} - {usage_trend[-1]['year_month']}",
            "latest_month": latest,
            "previous_month": previous
        }
        
        if previous:
            request_change = ((latest["total_requests"] - previous["total_requests"]) / previous["total_requests"] * 100) if previous["total_requests"] > 0 else 0
            cost_change = ((latest["total_cost"] - previous["total_cost"]) / previous["total_cost"] * 100) if previous["total_cost"] > 0 else 0
            
            trend_data.update({
                "month_over_month_change": {
                    "requests": round(request_change, 1),
                    "cost": round(cost_change, 1)
                },
                "trend_direction": "上升" if request_change > 0 else "下降" if request_change < 0 else "持平"
            })
        
        return trend_data
    
    def _generate_cost_analysis(self, monthly_stats: Dict, usage_trend: List) -> Dict:
        """生成成本分析"""
        cost_per_request = (monthly_stats["total_cost"] / monthly_stats["total_requests"]) if monthly_stats["total_requests"] > 0 else 0
        cost_per_token = (monthly_stats["total_cost"] / monthly_stats["total_tokens"]) if monthly_stats["total_tokens"] > 0 else 0
        
        analysis = {
            "current_month_cost_efficiency": {
                "cost_per_request": round(cost_per_request, 4),
                "cost_per_token": round(cost_per_token, 6),
                "total_cost": monthly_stats["total_cost"]
            },
            "cost_breakdown": self._estimate_cost_breakdown(monthly_stats),
            "budget_projections": self._generate_budget_projections(usage_trend)
        }
        
        return analysis
    
    def _estimate_cost_breakdown(self, monthly_stats: Dict) -> Dict:
        """估算成本分布"""
        model_costs = {}
        total_cost = monthly_stats["total_cost"]
        
        # 简化的成本分布计算
        for model, requests in monthly_stats["model_usage"].items():
            model_percentage = requests / monthly_stats["total_requests"]
            model_costs[model] = round(total_cost * model_percentage, 2)
        
        return model_costs
    
    def _generate_budget_projections(self, usage_trend: List) -> Dict:
        """生成预算预测"""
        if len(usage_trend) < 2:
            return {"projection_available": False}
        
        # 基于最近趋势预测下月成本
        recent_costs = [month["total_cost"] for month in usage_trend[-3:]]  # 最近3个月
        avg_growth = 0
        
        if len(recent_costs) >= 2:
            growth_rates = []
            for i in range(1, len(recent_costs)):
                if recent_costs[i-1] > 0:
                    growth = (recent_costs[i] - recent_costs[i-1]) / recent_costs[i-1]
                    growth_rates.append(growth)
            
            avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0
        
        current_cost = recent_costs[-1] if recent_costs else 0
        projected_cost = current_cost * (1 + avg_growth)
        
        return {
            "projection_available": True,
            "next_month_projection": round(projected_cost, 2),
            "projected_growth_rate": round(avg_growth * 100, 1),
            "confidence_level": "中等" if len(recent_costs) >= 3 else "较低"
        }
    
    def _generate_recommendations(self, monthly_stats: Dict, usage_trend: List) -> List[Dict]:
        """生成使用建议"""
        recommendations = []
        
        # 成功率建议
        if monthly_stats["success_rate"] < 95:
            recommendations.append({
                "type": "warning",
                "category": "成功率",
                "title": "API成功率偏低",
                "description": f"当前成功率 {monthly_stats['success_rate']}%，建议检查网络连接和API配置",
                "priority": "高"
            })
        
        # 成本趋势建议
        if len(usage_trend) >= 2:
            latest_change = usage_trend[-1]["total_cost"] - usage_trend[-2]["total_cost"]
            change_percent = (latest_change / usage_trend[-2]["total_cost"] * 100) if usage_trend[-2]["total_cost"] > 0 else 0
            
            if change_percent > 50:
                recommendations.append({
                    "type": "warning",
                    "category": "成本控制",
                    "title": "成本增长过快",
                    "description": f"本月成本较上月增长 {change_percent:.1f}%，建议审查使用模式",
                    "priority": "高"
                })
            elif change_percent > 20:
                recommendations.append({
                    "type": "info",
                    "category": "成本控制",
                    "title": "成本增长提醒",
                    "description": f"本月成本较上月增长 {change_percent:.1f}%，建议关注使用趋势",
                    "priority": "中"
                })
        
        # 使用频率建议
        if monthly_stats["daily_average"] > 100:
            recommendations.append({
                "type": "success",
                "category": "使用频率",
                "title": "高频使用用户",
                "description": "您是高频率用户，建议考虑批量优化和缓存策略以提升效率",
                "priority": "中"
            })
        
        # 模型使用建议
        if monthly_stats["model_usage"]:
            most_used = max(monthly_stats["model_usage"].items(), key=lambda x: x[1])
            if most_used[0] == "moonshot-v1-128k":
                recommendations.append({
                    "type": "info",
                    "category": "模型选择",
                    "title": "大模型使用建议",
                    "description": "您经常使用128K模型，确保任务确实需要大上下文以获得最佳性价比",
                    "priority": "低"
                })
        
        # 如果没有特别建议，给出通用建议
        if not recommendations:
            recommendations.append({
                "type": "success",
                "category": "总体评价",
                "title": "使用状况良好",
                "description": "您的API使用状况良好，继续保持当前的优化策略",
                "priority": "低"
            })
        
        return recommendations
    
    def _save_report(self, report: Dict, year_month: str):
        """保存报告到文件"""
        filename = f"kimi_usage_report_{year_month}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 报告已保存: {filepath}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
    
    def format_telegram_report(self, report: Dict) -> str:
        """格式化为Telegram消息"""
        summary = report["usage_summary"]
        trend = report["trend_analysis"]
        recommendations = report["recommendations"]
        
        # 基本统计
        message = f"""📊 **Kimi API {report['report_info']['report_period']} 使用报告**

🔢 **基本统计**
• 总请求次数: {summary['total_requests']:,}
• 总Token消耗: {summary['total_tokens']:,}
• 预估费用: ¥{summary['total_cost']:.2f}
• 成功率: {summary['success_rate']}%

📈 **使用分析**
• 日均请求: {summary['daily_average']:.1f} 次
• 峰值日期: {summary['peak_usage_day'] or '暂无数据'}
"""
        
        # 趋势分析
        if trend.get("analysis_available") and "month_over_month_change" in trend:
            change = trend["month_over_month_change"]
            message += f"""
📊 **趋势分析**
• 环比变化: {change['requests']:.1f}% (请求数)
• 成本变化: {change['cost']:.1f}% (费用)
• 趋势方向: {trend['trend_direction']}
"""
        
        # 预算预测
        budget = report["cost_analysis"]["budget_projections"]
        if budget.get("projection_available"):
            message += f"""
💰 **预算预测**
• 下月预测: ¥{budget['next_month_projection']:.2f}
• 预测增长率: {budget['projected_growth_rate']:.1f}%
"""
        
        # 重要建议（只显示高优先级）
        high_priority_rec = [r for r in recommendations if r["priority"] == "高"]
        if high_priority_rec:
            message += f"""
⚠️ **重要提醒**
"""
            for rec in high_priority_rec[:2]:  # 最多显示2个
                message += f"• {rec['title']}: {rec['description']}\n"
        
        message += f"""
📅 **报告生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 详细报告已保存至本地文件
"""
        
        return message

# 使用示例
if __name__ == "__main__":
    generator = KimiReportGenerator()
    
    # 生成当前月份报告
    current_month = datetime.datetime.now().strftime("%Y-%m")
    report = generator.generate_monthly_report(current_month)
    
    print("📊 月度报告生成完成")
    print(f"📈 总请求数: {report['usage_summary']['total_requests']:,}")
    print(f"💰 总费用: ¥{report['usage_summary']['total_cost']:.2f}")
    
    # 显示Telegram格式的报告
    telegram_message = generator.format_telegram_report(report)
    print("\n📱 Telegram消息格式:")
    print(telegram_message)