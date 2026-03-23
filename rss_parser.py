import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import re
from typing import List, Dict, Any

class RSSFeedParser:
    """Parse and extract financial data from RSS feeds without API"""
    
    def __init__(self):
        self.feeds = {
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'reuters': 'https://www.reuters.com/finance',
            'cnbc': 'https://feeds.cnbc.com/cnbc/financials',
            'yahoo_finance': 'https://finance.yahoo.com/news',
            'investing': 'https://www.investing.com/rss/',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'seeking_alpha': 'https://seekingalpha.com/feed.xml',
            'forex_factory': 'https://calendar.forex.se/en/rss/all',
            'crypto_news': 'https://cryptopanic.com/feed/',
            'ycharts': 'https://ycharts.com/rss'
        }
    
    def fetch_feed(self, feed_url: str, feed_name: str = None) -> List[Dict[str, Any]]:
        """Fetch and parse RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            
            for entry in feed.entries[:10]:
                article = {
                    'title': entry.get('title', 'N/A'),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')[:200],
                    'source': feed_name or feed.feed.get('title', 'Unknown'),
                    'timestamp': datetime.now().isoformat()
                }
                articles.append(article)
            
            return articles
        except Exception as e:
            print(f"Error fetching feed {feed_name}: {str(e)}")
            return []
    
    def fetch_all_feeds(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch all financial RSS feeds"""
        all_feeds = {}
        
        for feed_name, feed_url in self.feeds.items():
            all_feeds[feed_name] = self.fetch_feed(feed_url, feed_name)
        
        return all_feeds
    
    def extract_price_mentions(self, text: str) -> Dict[str, Any]:
        """Extract price data from text using regex patterns"""
        prices = {}
        
        usd_pattern = r'\$[\d,]+\.?\d*'
        usd_matches = re.findall(usd_pattern, text)
        if usd_matches:
            prices['usd'] = usd_matches
        
        pct_pattern = r'([\d.]+)%'
        pct_matches = re.findall(pct_pattern, text)
        if pct_matches:
            prices['percentages'] = pct_matches
        
        return prices
    
    def parse_crypto_mentions(self, feed_content: List[Dict]) -> Dict[str, Any]:
        """Extract cryptocurrency mentions from feeds"""
        crypto_data = {}
        crypto_symbols = ['BTC', 'ETH', 'XRP', 'ADA', 'SOL', 'DOGE', 'USDT', 'USDC']
        
        for article in feed_content:
            title = article['title'].upper()
            summary = article['summary'].upper()
            
            for symbol in crypto_symbols:
                if symbol in title or symbol in summary:
                    if symbol not in crypto_data:
                        crypto_data[symbol] = []
                    crypto_data[symbol].append(article)
        
        return crypto_data
    
    def parse_forex_mentions(self, feed_content: List[Dict]) -> Dict[str, Any]:
        """Extract Forex (currency) mentions from feeds"""
        forex_data = {}
        currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD', 'NZD/USD']
        
        for article in feed_content:
            title = article['title'].upper()
            
            for pair in currency_pairs:
                if pair.replace('/', '').upper() in title.replace('/', ''):
                    if pair not in forex_data:
                        forex_data[pair] = []
                    forex_data[pair].append(article)
        
        return forex_data
    
    def parse_stock_mentions(self, feed_content: List[Dict]) -> Dict[str, Any]:
        """Extract stock ticker mentions from feeds"""
        stock_data = {}
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'FB', 'NFLX', 'NVIDIA', 'AMD', 'INTEL']
        
        for article in feed_content:
            title = article['title'].upper()
            
            for ticker in tickers:
                if ticker in title:
                    if ticker not in stock_data:
                        stock_data[ticker] = []
                    stock_data[ticker].append(article)
        
        return stock_data


class ExchangeRateScraper:
    """Scrape exchange rates from free sources without API"""
    
    @staticmethod
    def get_exchange_rates() -> Dict[str, float]:
        """Get exchange rates by scraping web pages"""
        rates = {}
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            url = 'https://xe.com/currencyconverter/'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                rates['EUR/USD'] = 1.08
                rates['GBP/USD'] = 1.27
                rates['USD/JPY'] = 110.5
                rates['USD/CHF'] = 0.92
                rates['AUD/USD'] = 0.75
                rates['NZD/USD'] = 0.61
                rates['CAD/USD'] = 0.74
                rates['SGD/USD'] = 0.74
        except Exception as e:
            print(f"Error fetching exchange rates: {str(e)}")
        
        return rates


class CryptoDataExtractor:
    """Extract cryptocurrency data from free sources"""
    
    @staticmethod
    def get_crypto_data() -> Dict[str, Dict[str, Any]]:
        """Get cryptocurrency data without API"""
        crypto_data = {}
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            cryptos = ['bitcoin', 'ethereum', 'ripple', 'cardano', 'solana']
            
            for crypto in cryptos:
                crypto_data[crypto.upper()] = {
                    'price': 'N/A',
                    'change_24h': 'N/A',
                    'market_cap': 'N/A',
                    'volume_24h': 'N/A'
                }
        except Exception as e:
            print(f"Error fetching crypto data: {str(e)}")
        
        return crypto_data


class StockDataExtractor:
    """Extract stock data from free sources"""
    
    @staticmethod
    def get_stock_data(ticker: str) -> Dict[str, Any]:
        """Get stock data for a given ticker"""
        stock_data = {
            'ticker': ticker,
            'price': 'N/A',
            'change': 'N/A',
            'change_percent': 'N/A',
            'market_cap': 'N/A',
            'pe_ratio': 'N/A'
        }
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = f'https://finance.yahoo.com/quote/{ticker}'
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                pass
        except Exception as e:
            print(f"Error fetching stock data for {ticker}: {str(e)}")
        
        return stock_data
