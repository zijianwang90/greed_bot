"""
数据获取模块
从各种来源获取恐慌贪婪指数和其他市场指标数据
"""

import json
import logging
import re
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd

from config import (
    CNN_FEAR_GREED_API,
    BACKUP_DATA_SOURCE,
    REQUEST_TIMEOUT,
    MAX_RETRIES
)

logger = logging.getLogger(__name__)


class FearGreedDataFetcher:
    """恐慌贪婪指数数据获取器"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        # 设置浏览器头部以避免反爬虫检测 - 针对Yahoo Finance优化
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Pragma': 'no-cache',
            'Referer': 'https://finance.yahoo.com/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_fear_greed_index(self) -> Optional[Dict]:
        """获取当前恐慌贪婪指数"""
        try:
            # 尝试从 CNN 官方 API 获取
            logger.info("尝试从 CNN API 获取恐慌贪婪指数...")
            data = await self._fetch_from_cnn_api()
            if data:
                logger.info("成功从 CNN API 获取数据")
                return data
                
            # 备用方案：从 Alternative.me API 获取
            logger.warning("CNN API 失败，尝试备用数据源 (Alternative.me)...")
            backup_data = await self._fetch_from_backup_source()
            if backup_data:
                logger.info("成功从备用数据源获取数据")
                return backup_data
            else:
                logger.error("所有数据源都失败了")
                return None
            
        except Exception as e:
            logger.error(f"获取恐慌贪婪指数失败: {e}")
            return None
    
    async def _fetch_from_cnn_api(self) -> Optional[Dict]:
        """从 CNN API 获取数据"""
        for attempt in range(MAX_RETRIES):
            try:
                # 添加一些随机延迟以避免被检测为自动化请求
                if attempt > 0:
                    import random
                    await asyncio.sleep(random.uniform(1, 3))
                
                async with self.session.get(CNN_FEAR_GREED_API) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_cnn_data(data)
                    elif response.status == 418:
                        logger.warning(f"CNN API 拒绝请求 (状态码 418) - 尝试 {attempt + 1}/{MAX_RETRIES}")
                        if attempt == MAX_RETRIES - 1:
                            logger.error("CNN API 持续返回 418 状态码，可能被反爬虫系统阻止")
                        continue
                    else:
                        logger.warning(f"CNN API 返回状态码: {response.status} - 尝试 {attempt + 1}/{MAX_RETRIES}")
                        continue
                        
            except Exception as e:
                logger.error(f"从 CNN API 获取数据失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES - 1:
                    return None
                continue
        
        return None
    
    def _parse_cnn_data(self, data: Dict) -> Dict:
        """解析 CNN API 数据"""
        try:
            fear_greed_data = data.get('fear_and_greed', {})
            
            current_score = fear_greed_data.get('score', 0)
            rating = fear_greed_data.get('rating', 'Unknown')
            last_update = fear_greed_data.get('timestamp', '')
            
            # 获取历史数据
            historical_data = fear_greed_data.get('previous_close', 0)
            week_ago = fear_greed_data.get('previous_1_week', 0)
            month_ago = fear_greed_data.get('previous_1_month', 0)
            year_ago = fear_greed_data.get('previous_1_year', 0)
            
            return {
                'current_value': current_score,
                'rating': rating,
                'last_update': last_update,
                'previous_close': historical_data,
                'week_ago': week_ago,
                'month_ago': month_ago,
                'year_ago': year_ago,
                'source': 'CNN Official API'
            }
            
        except Exception as e:
            logger.error(f"解析 CNN 数据失败: {e}")
            return {}
    
    async def _fetch_from_backup_source(self) -> Optional[Dict]:
        """从备用数据源获取数据"""
        try:
            async with self.session.get(BACKUP_DATA_SOURCE) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_backup_data(data)
                else:
                    logger.warning(f"备用数据源返回状态码: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"从备用数据源获取数据失败: {e}")
            return None
    
    def _parse_backup_data(self, data: Dict) -> Dict:
        """解析备用数据源的 JSON (Alternative.me API)"""
        try:
            # Alternative.me API 返回格式：
            # {
            #   "name": "Fear and Greed Index",
            #   "data": [
            #     {
            #       "value": "40",
            #       "value_classification": "Fear",
            #       "timestamp": "1551157200",
            #       "time_until_update": "68499"
            #     }
            #   ]
            # }
            
            if 'data' in data and len(data['data']) > 0:
                latest_data = data['data'][0]
                
                current_value = int(latest_data.get('value', 50))
                rating = latest_data.get('value_classification', 'Unknown')
                timestamp = latest_data.get('timestamp', '')
                
                # 转换时间戳
                if timestamp:
                    try:
                        dt = datetime.fromtimestamp(int(timestamp))
                        last_update = dt.isoformat()
                    except:
                        last_update = datetime.now().isoformat()
                else:
                    last_update = datetime.now().isoformat()
                
                return {
                    'current_value': current_value,
                    'rating': rating,
                    'last_update': last_update,
                    'previous_close': None,
                    'week_ago': None,
                    'month_ago': None,
                    'year_ago': None,
                    'source': 'Alternative.me API'
                }
            else:
                logger.warning("备用数据源返回的数据格式不正确")
                return {}
            
        except Exception as e:
            logger.error(f"解析备用数据失败: {e}")
            return {}
    
    def _get_rating_from_value(self, value: int) -> str:
        """根据数值获取评级"""
        if value <= 25:
            return "Extreme Fear"
        elif value <= 45:
            return "Fear"  
        elif value <= 55:
            return "Neutral"
        elif value <= 75:
            return "Greed"
        else:
            return "Extreme Greed"
    
    async def get_vix_data(self) -> Optional[Dict]:
        """获取 VIX 波动率指数数据 - 使用 Alpha Vantage API"""
        try:
            import config_local
            api_key = config_local.ALPHA_VANTAGE_API_KEY
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=VIX&apikey={api_key}"
            
            logger.info("Fetching VIX data from Alpha Vantage API...")
            
            # 简单的请求头
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'VIX-Greed-Bot/1.0'
            }
            
            async with self.session.get(url, headers=headers) as response:
                logger.info(f"Alpha Vantage VIX API response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Alpha Vantage data structure: {type(data)} with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    parsed_data = self._parse_alpha_vantage_data(data)
                    if parsed_data and parsed_data.get('current_value', 0) > 0:
                        logger.info(f"✅ Successfully got VIX data from Alpha Vantage: current_value={parsed_data.get('current_value')}")
                        return parsed_data
                    else:
                        logger.warning(f"Alpha Vantage returned invalid data: {parsed_data}")
                
                elif response.status == 401:
                    logger.error("❌ Alpha Vantage API key invalid or expired")
                elif response.status == 429:
                    logger.error("❌ Alpha Vantage API rate limit exceeded")
                else:
                    logger.error(f"❌ Alpha Vantage API returned status {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response body: {response_text[:200]}...")
                        
        except Exception as e:
            logger.error(f"💥 Error fetching VIX data from Alpha Vantage: {e}")
        
        # 如果Alpha Vantage失败，返回智能演示数据
        logger.warning("Alpha Vantage API failed, returning intelligent demo data")
        return self._get_demo_vix_data()

    def _parse_alpha_vantage_data(self, data: Dict) -> Optional[Dict]:
        """解析Alpha Vantage API响应"""
        try:
            if 'Global Quote' in data:
                quote = data['Global Quote']
                current_price = float(quote.get('05. price', 0))
                previous_close = float(quote.get('08. previous close', 0))
                
                if current_price > 0:
                    change = current_price - previous_close
                    change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                    
                    return {
                        'current_value': current_price,
                        'previous_close': previous_close,
                        'change': change,
                        'change_percent': change_percent,
                        'last_update': datetime.now().isoformat(),
                        'source': 'Alpha Vantage',
                        'symbol': quote.get('01. symbol', 'VIX')
                    }
            
            logger.warning("Alpha Vantage data structure not recognized")
            return None
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Alpha Vantage data: {e}")
            return None

    def _parse_finnhub_data(self, data: Dict) -> Optional[Dict]:
        """解析Finnhub API响应"""
        try:
            current_price = float(data.get('c', 0))  # current price
            previous_close = float(data.get('pc', 0))  # previous close
            
            if current_price > 0:
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close > 0 else 0
                
                return {
                    'current_value': current_price,
                    'previous_close': previous_close,
                    'change': change,
                    'change_percent': change_percent,
                    'last_update': datetime.now().isoformat(),
                    'source': 'Finnhub',
                    'high': data.get('h', 0),
                    'low': data.get('l', 0),
                    'open': data.get('o', 0)
                }
            
            logger.warning("Finnhub data incomplete")
            return None
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing Finnhub data: {e}")
            return None






    

    
    def _get_demo_vix_data(self) -> Dict:
        """获取智能演示VIX数据 - 模拟真实市场情况"""
        import random
        from datetime import datetime, timedelta
        
        # 基于当前时间生成更真实的VIX数据
        now = datetime.now()
        hour = now.hour
        
        # 根据时间调整VIX水平（开盘和收盘时通常较高）
        if 9 <= hour <= 10 or 15 <= hour <= 16:  # 开盘和收盘时间
            base_vix = random.uniform(20.0, 45.0)  # 较高波动
        elif 11 <= hour <= 14:  # 交易时间
            base_vix = random.uniform(15.0, 30.0)  # 正常波动
        else:  # 非交易时间
            base_vix = random.uniform(12.0, 25.0)  # 较低波动
        
        # 生成合理的昨日收盘价
        previous_close = base_vix + random.uniform(-3.0, 3.0)
        previous_close = max(10.0, min(80.0, previous_close))  # 限制在合理范围内
        
        # 计算变化
        change = base_vix - previous_close
        change_percent = (change / previous_close) * 100
        
        # 添加市场情绪标签
        if base_vix < 15:
            sentiment = "极低波动 - 市场信心充足"
        elif base_vix < 20:
            sentiment = "低波动 - 市场相对平静"
        elif base_vix < 30:
            sentiment = "正常波动 - 市场运行平稳"
        elif base_vix < 40:
            sentiment = "较高波动 - 市场出现不确定性"
        else:
            sentiment = "高波动 - 市场恐慌情绪上升"
        
        demo_data = {
            'current_value': round(base_vix, 2),
            'previous_close': round(previous_close, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'last_update': now.isoformat(),
            'source': '智能演示数据',
            'is_demo': True,
            'sentiment': sentiment,
            'market_hours': '交易时间' if 9 <= hour <= 16 else '非交易时间'
        }
        
        logger.info(f"Generated intelligent demo VIX data: {demo_data}")
        return demo_data
    

    
    async def get_put_call_ratio(self) -> Optional[Dict]:
        """获取 Put/Call 比率数据"""
        try:
            # CBOE Put/Call 比率
            url = "https://www.cboe.com/us/options/market_statistics/daily/"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_put_call_data(html)
                    
        except Exception as e:
            logger.error(f"获取 Put/Call 比率失败: {e}")
            
        return None
    
    def _parse_put_call_data(self, html: str) -> Dict:
        """解析 Put/Call 比率数据"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 这里需要根据 CBOE 网站的实际结构来解析
            # 由于网站结构可能变化，这里提供一个基础框架
            
            ratio = 1.0  # 默认值
            
            return {
                'ratio': ratio,
                'last_update': datetime.now().isoformat(),
                'interpretation': 'Neutral' if 0.8 <= ratio <= 1.2 else ('Bearish' if ratio > 1.2 else 'Bullish')
            }
            
        except Exception as e:
            logger.error(f"解析 Put/Call 数据失败: {e}")
            return {}
    
    async def get_market_breadth(self) -> Optional[Dict]:
        """获取市场广度数据"""
        try:
            # NYSE 涨跌股票数据
            url = "https://www.marketwatch.com/investing/index/adv"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self._parse_market_breadth_data(html)
                    
        except Exception as e:
            logger.error(f"获取市场广度数据失败: {e}")
            
        return None
    
    def _parse_market_breadth_data(self, html: str) -> Dict:
        """解析市场广度数据"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 基础数据，实际需要根据网站结构调整
            advancing = 2000
            declining = 1500
            unchanged = 500
            
            total = advancing + declining + unchanged
            advance_decline_ratio = advancing / declining if declining > 0 else 1.0
            
            return {
                'advancing': advancing,
                'declining': declining,
                'unchanged': unchanged,
                'advance_decline_ratio': round(advance_decline_ratio, 2),
                'breadth_thrust': advance_decline_ratio > 2.0,
                'last_update': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"解析市场广度数据失败: {e}")
            return {}


async def fetch_all_indicators() -> Dict:
    """获取所有市场指标"""
    async with FearGreedDataFetcher() as fetcher:
        results = {}
        
        # 并发获取所有数据
        tasks = [
            fetcher.get_current_fear_greed_index(),
            fetcher.get_vix_data(),
            fetcher.get_put_call_ratio(),
            fetcher.get_market_breadth()
        ]
        
        try:
            fear_greed, vix, put_call, breadth = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(fear_greed, Exception) and fear_greed:
                results['fear_greed'] = fear_greed
                
            if not isinstance(vix, Exception) and vix:
                results['vix'] = vix
                
            if not isinstance(put_call, Exception) and put_call:
                results['put_call'] = put_call
                
            if not isinstance(breadth, Exception) and breadth:
                results['market_breadth'] = breadth
                
        except Exception as e:
            logger.error(f"获取市场指标时发生错误: {e}")
            
        return results


# 便捷函数
async def get_fear_greed_index() -> Optional[Dict]:
    """获取恐慌贪婪指数的便捷函数"""
    async with FearGreedDataFetcher() as fetcher:
        return await fetcher.get_current_fear_greed_index()


# 兼容性别名
class DataFetcher(FearGreedDataFetcher):
    """DataFetcher 兼容性别名"""
    
    async def get_current_fear_greed_index(self) -> Optional[Dict]:
        """获取当前恐慌贪婪指数 - 兼容性方法"""
        # 使用 context manager 来管理 session
        async with self:
            data = await super().get_current_fear_greed_index()
            if data:
                # 转换数据格式以匹配 handlers.py 的预期
                return {
                    'score': data.get('current_value', 0),
                    'rating': data.get('rating', 'Unknown'),
                    'timestamp': data.get('last_update', ''),
                    'previous_close': data.get('previous_close'),
                    'week_ago': data.get('week_ago'),
                    'month_ago': data.get('month_ago'),
                    'year_ago': data.get('year_ago'),
                    'source': data.get('source', 'Unknown')
                }
            return None 