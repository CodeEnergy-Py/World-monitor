import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class DatabaseManager:
    """Manage SQLite database for storing financial data"""
    
    def __init__(self, db_name: str = 'world_monitor.db'):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE,
                source TEXT,
                summary TEXT,
                published TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_pair TEXT NOT NULL,
                rate REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crypto_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL,
                change_24h REAL,
                market_cap TEXT,
                volume_24h REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                price REAL,
                change REAL,
                change_percent REAL,
                market_cap TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                symbol TEXT NOT NULL,
                quantity REAL,
                purchase_price REAL,
                asset_type TEXT,
                purchase_date TIMESTAMP,
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT,
                target_price REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_article(self, title: str, link: str, source: str, summary: str, published: str) -> bool:
        """Insert article into database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO articles (title, link, source, summary, published)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, link, source, summary, published))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting article: {str(e)}")
            return False
    
    def get_recent_articles(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent articles from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, title, link, source, summary, published, fetched_at
            FROM articles
            ORDER BY fetched_at DESC
            LIMIT ?
        ''', (limit,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'title': row[1],
                'link': row[2],
                'source': row[3],
                'summary': row[4],
                'published': row[5],
                'fetched_at': row[6]
            })
        
        conn.close()
        return articles
    
    def insert_exchange_rate(self, currency_pair: str, rate: float) -> bool:
        """Insert exchange rate"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO exchange_rates (currency_pair, rate)
                VALUES (?, ?)
            ''', (currency_pair, rate))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting exchange rate: {str(e)}")
            return False
    
    def get_latest_exchange_rates(self) -> Dict[str, float]:
        """Get latest exchange rates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT currency_pair, rate
            FROM exchange_rates
            WHERE timestamp = (SELECT MAX(timestamp) FROM exchange_rates)
        ''')
        
        rates = {}
        for row in cursor.fetchall():
            rates[row[0]] = row[1]
        
        conn.close()
        return rates
    
    def insert_crypto_data(self, symbol: str, price: float, change_24h: float, 
                          market_cap: str, volume_24h: float) -> bool:
        """Insert cryptocurrency data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO crypto_data (symbol, price, change_24h, market_cap, volume_24h)
                VALUES (?, ?, ?, ?, ?)
            ''', (symbol, price, change_24h, market_cap, volume_24h))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting crypto data: {str(e)}")
            return False
    
    def insert_stock_data(self, ticker: str, price: float, change: float, 
                         change_percent: float, market_cap: str) -> bool:
        """Insert stock data"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_data (ticker, price, change, change_percent, market_cap)
                VALUES (?, ?, ?, ?, ?)
            ''', (ticker, price, change, change_percent, market_cap))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting stock data: {str(e)}")
            return False
    
    def add_portfolio_item(self, user_id: str, symbol: str, quantity: float, 
                          purchase_price: float, asset_type: str, notes: str = None) -> bool:
        """Add item to portfolio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO portfolio (user_id, symbol, quantity, purchase_price, asset_type, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, symbol, quantity, purchase_price, asset_type, notes))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding portfolio item: {str(e)}")
            return False
    
    def get_portfolio(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, quantity, purchase_price, asset_type, purchase_date, notes
            FROM portfolio
            WHERE user_id = ?
            ORDER BY purchase_date DESC
        ''', (user_id,))
        
        portfolio = []
        for row in cursor.fetchall():
            portfolio.append({
                'id': row[0],
                'symbol': row[1],
                'quantity': row[2],
                'purchase_price': row[3],
                'asset_type': row[4],
                'purchase_date': row[5],
                'notes': row[6]
            })
        
        conn.close()
        return portfolio
    
    def set_price_alert(self, symbol: str, alert_type: str, target_price: float) -> bool:
        """Set price alert for a symbol"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_alerts (symbol, alert_type, target_price)
                VALUES (?, ?, ?)
            ''', (symbol, alert_type, target_price))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting price alert: {str(e)}")
            return False
    
    def get_price_alerts(self) -> List[Dict[str, Any]]:
        """Get all active price alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, alert_type, target_price
            FROM price_alerts
            WHERE is_active = 1
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'symbol': row[1],
                'alert_type': row[2],
                'target_price': row[3]
            })
        
        conn.close()
        return alerts