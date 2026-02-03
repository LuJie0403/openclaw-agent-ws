import pymysql
import pandas as pd
import json
from datetime import datetime, timedelta
import configparser

class ExpenseDatabase:
    def __init__(self, config_file='db_config.ini'):
        self.config = self.load_config(config_file)
        self.connection = None
    
    def load_config(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config['mysql']
    
    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset='utf8mb4'
            )
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def get_monthly_stats(self, year=None):
        if not year:
            year = datetime.now().year
        
        query = """
        SELECT 
            DATE_FORMAT(expense_date, '%Y-%m') as month,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM personal_expenses_final 
        WHERE YEAR(expense_date) = %s
        GROUP BY DATE_FORMAT(expense_date, '%Y-%m')
        ORDER BY month
        """
        
        df = pd.read_sql(query, self.connection, params=[year])
        return df.to_dict('records')
    
    def get_yearly_stats(self):
        query = """
        SELECT 
            YEAR(expense_date) as year,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM personal_expenses_final 
        GROUP BY YEAR(expense_date)
        ORDER BY year
        """
        
        df = pd.read_sql(query, self.connection)
        return df.to_dict('records')
    
    def get_category_analysis(self, start_date=None, end_date=None):
        query = """
        SELECT 
            pet.type_name as category,
            COUNT(*) as transaction_count,
            SUM(pef.amount) as total_amount,
            AVG(pef.amount) as avg_amount,
            ROUND(SUM(pef.amount) * 100.0 / (SELECT SUM(amount) FROM personal_expenses_final WHERE (%s IS NULL OR expense_date >= %s) AND (%s IS NULL OR expense_date <= %s)), 2) as percentage
        FROM personal_expenses_final pef
        JOIN personal_expenses_type pet ON pef.expense_type_id = pet.id
        WHERE (%s IS NULL OR pef.expense_date >= %s) AND (%s IS NULL OR pef.expense_date <= %s)
        GROUP BY pet.type_name
        ORDER BY total_amount DESC
        """
        
        params = [start_date, start_date, end_date, end_date, start_date, start_date, end_date, end_date]
        df = pd.read_sql(query, self.connection, params=params)
        return df.to_dict('records')
    
    def get_trend_data(self, category=None, days=365):
        query = """
        SELECT 
            DATE(expense_date) as date,
            SUM(amount) as daily_total
        FROM personal_expenses_final pef
        JOIN personal_expenses_type pet ON pef.expense_type_id = pet.id
        WHERE expense_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        AND (%s IS NULL OR pet.type_name = %s)
        GROUP BY DATE(expense_date)
        ORDER BY date
        """
        
        params = [days, category, category]
        df = pd.read_sql(query, self.connection, params=params)
        return df.to_dict('records')
    
    def get_recent_expenses(self, limit=10):
        query = """
        SELECT 
            pef.id,
            pef.expense_date,
            pef.amount,
            pet.type_name as category,
            pef.description
        FROM personal_expenses_final pef
        JOIN personal_expenses_type pet ON pef.expense_type_id = pet.id
        ORDER BY pef.expense_date DESC, pef.id DESC
        LIMIT %s
        """
        
        df = pd.read_sql(query, self.connection, params=[limit])
        return df.to_dict('records')
    
    def close(self):
        if self.connection:
            self.connection.close()