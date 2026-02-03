#!/usr/bin/env python3
"""
路杰个人支出数据看板 - 全球可访问WEB服务
基于 iterlife4openclaw 数据库
技术栈：Flask + MySQL + Bootstrap + Chart.js
"""

import mysql.connector
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
import os

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': '120.27.250.73',
    'user': 'openclaw_aws',
    'password': '9!wQSw@12sq',
    'database': 'iterlife4openclaw',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def get_expense_summary():
    """获取支出汇总数据"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 总体统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                ROUND(SUM(trans_amount), 2) as total_amount,
                MIN(trans_date) as start_date,
                MAX(trans_date) as end_date
            FROM personal_expenses_final;
        """)
        summary = cursor.fetchone()
        
        # 月度统计
        cursor.execute("""
            SELECT 
                trans_year,
                trans_month,
                COUNT(*) as record_count,
                ROUND(SUM(trans_amount), 2) as monthly_amount
            FROM personal_expenses_final
            GROUP BY trans_year, trans_month
            ORDER BY trans_year DESC, trans_month DESC
            LIMIT 24;
        """)
        monthly_data = cursor.fetchall()
        
        # 年度统计
        cursor.execute("""
            SELECT 
                trans_year,
                COUNT(*) as record_count,
                ROUND(SUM(trans_amount), 2) as yearly_amount
            FROM personal_expenses_final
            GROUP BY trans_year
            ORDER BY trans_year DESC;
        """)
        yearly_data = cursor.fetchall()
        
        return {
            'summary': summary,
            'monthly': monthly_data,
            'yearly': yearly_data
        }
    except Exception as e:
        print(f"数据查询失败: {e}")
        return {}
    finally:
        if conn:
            conn.close()

@app.route('/')
def index():
    """主页 - 显示看板"""
    data = get_expense_summary()
    return render_template('expense_dashboard.html', data=data)

@app.route('/api/data')
def api_data():
    """API接口 - 返回JSON数据"""
    data = get_expense_summary()
    return jsonify(data)

@app.route('/api/monthly')
def api_monthly():
    """API接口 - 返回月度数据"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': '数据库连接失败'})
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                trans_year,
                trans_month,
                COUNT(*) as record_count,
                ROUND(SUM(trans_amount), 2) as monthly_amount,
                AVG(trans_amount) as avg_amount
            FROM personal_expenses_final
            GROUP BY trans_year, trans_month
            ORDER BY trans_year DESC, trans_month DESC
            LIMIT 36;
        """)
        data = cursor.fetchall()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if conn:
            conn.close()

@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 启动路杰个人支出数据看板服务...")
    print("📊 基于 iterlife4openclaw 数据库")
    print("🌐 全球可访问地址即将生成...")
    
    # 启动服务
    app.run(host='0.0.0.0', port=8080, debug=False)