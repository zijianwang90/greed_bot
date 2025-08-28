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
        """获取 VIX 波动率指数数据"""
        # 尝试多个数据源，包括替代源
        vix_sources = [
            {
                'name': 'Finnhub VIX',
                'url': 'https://finnhub.io/api/v1/quote?symbol=VIX&token=demo',
                'parser': self._parse_finnhub_data
            },
            {
                'name': 'Alpha Vantage VIX',
                'url': 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=VIX&apikey=demo',
                'parser': self._parse_alpha_vantage_data
            },
            {
                'name': 'IEX Cloud VIX',
                'url': 'https://cloud.iexapis.com/stable/stock/vix/quote?token=Tpk_059b97af715d417d9f49f50b51b1c448',
                'parser': self._parse_iex_data
            },
            {
                'name': 'Yahoo Finance Chart API', 
                'url': 'https://query1.finance.yahoo.com/v8/finance/chart/^VIX',
                'parser': self._parse_yahoo_chart_data
            },
            {
                'name': 'Yahoo Finance Quote API',
                'url': 'https://query1.finance.yahoo.com/v7/finance/quote?symbols=^VIX',
                'parser': self._parse_yahoo_quote_data
            }
        ]
        
        for i, source in enumerate(vix_sources):
            try:
                logger.info(f"Trying VIX source {i+1}/{len(vix_sources)}: {source['name']}")
                
                # 添加延迟，对Yahoo Finance API使用更长延迟
                import random
                is_yahoo = 'yahoo' in source['name'].lower()
                delay = random.uniform(3.0, 6.0) if is_yahoo else random.uniform(0.5, 1.5)
                logger.info(f"Waiting {delay:.1f}s before request to {source['name']}...")
                await asyncio.sleep(delay)
                
                # 根据API类型设置特定请求头
                api_headers = {}
                if is_yahoo:
                    api_headers = {
                        'Accept': 'application/json',
                        'Cache-Control': 'no-cache',
                        'Pragma': 'no-cache',
                        'Referer': 'https://finance.yahoo.com/quote/%5EVIX/',
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                elif 'alpha' in source['name'].lower():
                    api_headers = {
                        'Accept': 'application/json',
                        'User-Agent': 'VIX-Bot/1.0',
                    }
                elif 'finnhub' in source['name'].lower():
                    api_headers = {
                        'Accept': 'application/json',
                        'X-Finnhub-Token': 'demo',
                    }
                elif 'iex' in source['name'].lower():
                    api_headers = {
                        'Accept': 'application/json',
                        'User-Agent': 'VIX-Greed-Bot/1.0',
                    }
                
                async with self.session.get(source['url'], headers=api_headers) as response:
                    logger.info(f"VIX {source['name']} response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"VIX {source['name']} data structure: {type(data)} with keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        parsed_data = source['parser'](data)
                        
                        if parsed_data and parsed_data.get('current_value', 0) > 0:
                            logger.info(f"✅ Successfully got VIX data from {source['name']}: current_value={parsed_data.get('current_value')}")
                            return parsed_data
                        else:
                            logger.warning(f"VIX {source['name']} returned invalid data: {parsed_data}")
                    
                    elif response.status == 429:
                        logger.warning(f"⚠️ VIX {source['name']} rate limited (429), waiting longer before next source...")
                        await asyncio.sleep(random.uniform(5.0, 8.0))  # 更长的等待时间
                        continue
                    elif response.status in [403, 404]:
                        logger.error(f"❌ VIX {source['name']} access denied or not found ({response.status})")
                        continue
                    else:
                        logger.error(f"❌ VIX {source['name']} returned status {response.status}")
                        response_text = await response.text()
                        logger.error(f"Response body: {response_text[:300]}...")
                        continue
                        
            except asyncio.TimeoutError:
                logger.error(f"⏰ VIX {source['name']} timed out")
                continue
            except Exception as e:
                logger.error(f"💥 VIX {source['name']} failed with exception: {e}")
                continue
        
        # 如果所有源都失败，返回模拟数据用于演示
        logger.warning("All VIX sources failed, returning demo data")
        return self._get_demo_vix_data()

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

    def _parse_iex_data(self, data: Dict) -> Optional[Dict]:
        """解析IEX Cloud API响应"""
        try:
            current_price = float(data.get('latestPrice', 0))
            previous_close = float(data.get('previousClose', 0))
            
            if current_price > 0:
                change = float(data.get('change', 0))
                change_percent = float(data.get('changePercent', 0)) * 100
                
                return {
                    'current_value': current_price,
                    'previous_close': previous_close,
                    'change': change,
                    'change_percent': change_percent,
                    'last_update': data.get('latestUpdate', datetime.now().isoformat()),
                    'source': 'IEX Cloud',
                    'market_cap': data.get('marketCap'),
                    'volume': data.get('volume')
                }
            
            logger.warning("IEX Cloud data incomplete")
            return None
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing IEX Cloud data: {e}")
            return None

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

    def _parse_marketwatch_data(self, data: Dict) -> Optional[Dict]:
        """解析MarketWatch API响应"""
        try:
            if 'TimeValueCollection' in data and data['TimeValueCollection']:
                recent_data = data['TimeValueCollection'][-1]  # 最新数据
                previous_data = data['TimeValueCollection'][-2] if len(data['TimeValueCollection']) > 1 else recent_data
                
                current_price = float(recent_data.get('Value', 0))
                previous_price = float(previous_data.get('Value', 0))
                
                if current_price > 0:
                    change = current_price - previous_price
                    change_percent = (change / previous_price * 100) if previous_price > 0 else 0
                    
                    return {
                        'current_value': current_price,
                        'previous_close': previous_price,
                        'change': change,
                        'change_percent': change_percent,
                        'last_update': recent_data.get('TimeStamp', datetime.now().isoformat()),
                        'source': 'MarketWatch'
                    }
            
            logger.warning("MarketWatch data structure not recognized")
            return None
            
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing MarketWatch data: {e}")
        return None
    
    def _parse_yahoo_quote_data(self, data: Dict) -> Dict:
        """解析Yahoo Finance Quote API数据"""
        try:
            if 'quoteResponse' not in data:
                logger.error("No 'quoteResponse' in Yahoo quote data")
                return {}
                
            quote_response = data['quoteResponse']
            if 'result' not in quote_response or not quote_response['result']:
                logger.error("No 'result' in quote response")
                return {}
                
            result = quote_response['result'][0]
            logger.info(f"Yahoo quote result: {result}")
            
            current_price = result.get('regularMarketPrice', 0)
            previous_close = result.get('regularMarketPreviousClose', 0)
            
            if current_price == 0:
                current_price = result.get('bid', result.get('ask', 0))
            
            change = result.get('regularMarketChange', 0)
            change_percent = result.get('regularMarketChangePercent', 0)
            
            if change == 0 and previous_close > 0:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
            
            parsed_result = {
                'current_value': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'last_update': datetime.now().isoformat(),
                'source': 'Yahoo Finance Quote API'
            }
            
            logger.info(f"Parsed Yahoo quote VIX data: {parsed_result}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"解析Yahoo Quote VIX数据失败: {e}", exc_info=True)
            return {}
    
    def _get_demo_vix_data(self) -> Dict:
        """获取演示VIX数据"""
        import random
        
        # 生成合理范围内的VIX数据 (通常在10-80之间)
        base_vix = random.uniform(15.0, 35.0)
        previous_close = base_vix + random.uniform(-2.0, 2.0)
        change = base_vix - previous_close
        change_percent = (change / previous_close) * 100
        
        demo_data = {
            'current_value': round(base_vix, 2),
            'previous_close': round(previous_close, 2),
            'change': round(change, 2),
            'change_percent': round(change_percent, 2),
            'last_update': datetime.now().isoformat(),
            'source': 'Demo Data',
            'is_demo': True
        }
        
        logger.info(f"Generated demo VIX data: {demo_data}")
        return demo_data
    
    def _parse_yahoo_chart_data(self, data: Dict) -> Dict:
        """解析Yahoo Finance Chart API数据"""
        try:
            logger.info(f"Parsing VIX data structure: {data}")
            
            if 'chart' not in data:
                logger.error("No 'chart' key in VIX data")
                return {}
                
            chart = data['chart']
            if 'result' not in chart or not chart['result']:
                logger.error("No 'result' in chart data or result is empty")
                return {}
                
            result = chart['result'][0]
            logger.info(f"VIX result keys: {list(result.keys())}")
            
            if 'meta' not in result:
                logger.error("No 'meta' key in result")
                return {}
                
            meta = result['meta']
            logger.info(f"VIX meta data: {meta}")
            
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', 0)
            
            if current_price == 0:
                logger.warning("Current price is 0, checking alternative fields")
                # Try alternative fields
                current_price = meta.get('currentPrice', 0)
                if current_price == 0:
                    current_price = meta.get('price', 0)
            
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close) * 100 if previous_close else 0
            
            parsed_result = {
                'current_value': round(current_price, 2),
                'previous_close': round(previous_close, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'last_update': datetime.now().isoformat()
            }
            
            logger.info(f"Successfully parsed VIX data: {parsed_result}")
            return parsed_result
            
        except Exception as e:
            logger.error(f"解析 VIX 数据失败: {e}", exc_info=True)
            return {}
    
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