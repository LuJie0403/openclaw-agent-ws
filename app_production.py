from flask import Flask, render_template, jsonify, request, send_file
from expense_analyzer import ExpenseDatabase
from datetime import datetime, timedelta
import json
import pandas as pd
import io
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'iterlife4openclaw'),
    'charset': 'utf8mb4'
}

def get_db():
    """获取数据库连接"""
    return ExpenseDatabase(DB_CONFIG)

@app.route('/health')
def health_check():
    """健康检查端点"""
    try:
        db = get_db()
        if db.connect():
            db.close()
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        else:
            return jsonify({'status': 'unhealthy', 'error': 'Database connection failed'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/')
def dashboard():
    """主仪表板页面"""
    return render_template('dashboard.html')

@app.route('/api/monthly-stats')
def monthly_stats():
    """获取月度统计数据"""
    year = request.args.get('year', type=int)
    
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        stats = db.get_monthly_stats(year)
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"获取月度统计数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/yearly-stats')
def yearly_stats():
    """获取年度统计数据"""
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        stats = db.get_yearly_stats()
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"获取年度统计数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/category-analysis')
def category_analysis():
    """获取分类分析数据"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        analysis = db.get_category_analysis(start_date, end_date)
        return jsonify(analysis)
    except Exception as e:
        app.logger.error(f"获取分类分析数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/trend-data')
def trend_data():
    """获取趋势数据"""
    category = request.args.get('category')
    days = request.args.get('days', 365, type=int)
    
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        trend = db.get_trend_data(category, days)
        return jsonify(trend)
    except Exception as e:
        app.logger.error(f"获取趋势数据失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/api/recent-expenses')
def recent_expenses():
    """获取最近支出记录"""
    limit = request.args.get('limit', 10, type=int)
    
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        expenses = db.get_recent_expenses(limit)
        return jsonify(expenses)
    except Exception as e:
        app.logger.error(f"获取最近支出记录失败: {e}")
        return jsonify({'error': '获取数据失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.route('/export/<format>')
def export_data(format):
    """导出数据"""
    if format not in ['csv', 'json']:
        return jsonify({'error': '不支持的导出格式'}), 400
    
    data_type = request.args.get('type', 'monthly')
    
    try:
        db = get_db()
        if not db.connect():
            return jsonify({'error': '数据库连接失败'}), 500
        
        # 获取数据
        if data_type == 'monthly':
            data = db.get_monthly_stats()
            filename = f'月支出统计_{datetime.now().strftime("%Y%m%d")}.{format}'
        elif data_type == 'yearly':
            data = db.get_yearly_stats()
            filename = f'年支出统计_{datetime.now().strftime("%Y%m%d")}.{format}'
        elif data_type == 'category':
            data = db.get_category_analysis()
            filename = f'分类支出分析_{datetime.now().strftime("%Y%m%d")}.{format}'
        else:
            return jsonify({'error': '无效的数据类型'}), 400
        
        # 生成文件
        if format == 'csv':
            df = pd.DataFrame(data)
            output = io.BytesIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        else:  # json
            output = io.BytesIO()
            output.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/json',
                as_attachment=True,
                download_name=filename
            )
            
    except Exception as e:
        app.logger.error(f"导出数据失败: {e}")
        return jsonify({'error': '导出失败'}), 500
    finally:
        if 'db' in locals():
            db.close()

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '页面未找到'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    # 生产环境使用Gunicorn，开发环境使用Flask内置服务器
    if os.getenv('FLASK_ENV') == 'development':
        app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        # 生产环境配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        # 配置日志
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/expense_dashboard.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Expense Dashboard startup')
        
        # 使用Gunicorn启动
        # gunicorn -w 4 -b 0.0.0.0:5000 app:app