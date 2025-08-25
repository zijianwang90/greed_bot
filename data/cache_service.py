"""
缓存服务模块
管理数据缓存逻辑，优先从数据库获取，只在必要时才请求API
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .database import get_cached_fear_greed_data, save_fear_greed_data_to_cache
from .fetcher import FearGreedDataFetcher

logger = logging.getLogger(__name__)


class CacheAwareFearGreedService:
    """缓存感知的恐慌贪婪指数服务"""
    
    def __init__(self, cache_timeout_minutes: int = 30):
        """
        初始化缓存服务
        
        Args:
            cache_timeout_minutes: 缓存过期时间（分钟），默认30分钟
        """
        self.cache_timeout_minutes = cache_timeout_minutes
        
    async def get_current_fear_greed_index(self, force_refresh: bool = False) -> Optional[Dict]:
        """
        获取当前恐慌贪婪指数，优先使用缓存
        
        Args:
            force_refresh: 是否强制刷新（跳过缓存）
            
        Returns:
            包含指数数据的字典，如果获取失败返回None
        """
        try:
            # 如果不强制刷新，先尝试从缓存获取
            if not force_refresh:
                logger.debug(f"检查缓存，超时时间: {self.cache_timeout_minutes}分钟")
                cached_data = await get_cached_fear_greed_data(self.cache_timeout_minutes)
                if cached_data:
                    logger.info(f"✅ 从缓存获取数据成功，缓存时间: {cached_data.get('cache_time')}")
                    return self._format_cached_data(cached_data)
                else:
                    logger.info("❌ 缓存中没有有效数据")
            else:
                logger.info("🔄 强制刷新，跳过缓存检查")
            
            # 缓存未命中或强制刷新，从API获取新数据
            logger.info("🌐 缓存未命中或过期，从API获取新数据...")
            fresh_data = await self._fetch_fresh_data()
            
            if fresh_data:
                # 保存到缓存
                logger.info(f"💾 保存新数据到缓存: Index={fresh_data.get('current_value') or fresh_data.get('score')}")
                save_success = await save_fear_greed_data_to_cache(fresh_data)
                if save_success:
                    logger.info("✅ 新数据已保存到缓存")
                else:
                    logger.warning("⚠️ 保存数据到缓存失败")
                return self._format_api_data(fresh_data)
            
            # API失败，尝试获取稍旧的缓存数据作为备用
            logger.warning("API获取失败，尝试获取较旧的缓存数据...")
            fallback_data = await get_cached_fear_greed_data(cache_timeout_minutes=180)  # 3小时内的数据
            if fallback_data:
                logger.info("使用较旧的缓存数据作为备用")
                fallback_data['is_stale'] = True
                return self._format_cached_data(fallback_data)
            
            logger.error("无法获取任何数据")
            return None
            
        except Exception as e:
            logger.error(f"获取恐慌贪婪指数失败: {e}")
            return None
    
    async def _fetch_fresh_data(self) -> Optional[Dict]:
        """从API获取新数据"""
        try:
            async with FearGreedDataFetcher() as fetcher:
                return await fetcher.get_current_fear_greed_index()
        except Exception as e:
            logger.error(f"API获取数据失败: {e}")
            return None
    
    def _format_cached_data(self, cached_data: Dict) -> Dict:
        """格式化缓存数据以匹配API响应格式"""
        return {
            'score': cached_data.get('current_value', 0),
            'rating': cached_data.get('rating', 'Unknown'),
            'timestamp': cached_data.get('last_update', ''),
            'previous_close': cached_data.get('previous_close'),
            'week_ago': cached_data.get('week_ago'),
            'month_ago': cached_data.get('month_ago'),
            'year_ago': cached_data.get('year_ago'),
            'source': cached_data.get('source', 'Unknown'),
            'cached': True,
            'cache_time': cached_data.get('cache_time'),
            'is_stale': cached_data.get('is_stale', False)
        }
    
    def _format_api_data(self, api_data: Dict) -> Dict:
        """格式化API数据"""
        return {
            'score': api_data.get('current_value', 0),
            'rating': api_data.get('rating', 'Unknown'),
            'timestamp': api_data.get('last_update', ''),
            'previous_close': api_data.get('previous_close'),
            'week_ago': api_data.get('week_ago'),
            'month_ago': api_data.get('month_ago'),
            'year_ago': api_data.get('year_ago'),
            'source': api_data.get('source', 'Unknown'),
            'cached': False,
            'fresh': True
        }
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态信息"""
        try:
            cached_data = await get_cached_fear_greed_data(cache_timeout_minutes=1440)  # 24小时内
            
            if cached_data:
                cache_age_minutes = (
                    datetime.utcnow() - datetime.fromisoformat(cached_data['cache_time'].replace('Z', '+00:00'))
                ).total_seconds() / 60
                
                return {
                    'has_cache': True,
                    'cache_age_minutes': int(cache_age_minutes),
                    'is_fresh': cache_age_minutes <= self.cache_timeout_minutes,
                    'last_update': cached_data.get('last_update'),  # 使用数据的实际更新时间，而不是缓存时间
                    'cache_time': cached_data.get('cache_time'),  # 保留缓存时间用于内部计算
                    'current_value': cached_data.get('current_value'),
                    'source': cached_data.get('source')
                }
            else:
                return {
                    'has_cache': False,
                    'cache_age_minutes': None,
                    'is_fresh': False,
                    'last_update': None,
                    'current_value': None,
                    'source': None
                }
                
        except Exception as e:
            logger.error(f"获取缓存状态失败: {e}")
            return {
                'has_cache': False,
                'error': str(e)
            }


class SmartDataFetcher:
    """智能数据获取器 - 兼容原有接口的缓存感知版本"""
    
    def __init__(self, cache_timeout_minutes: int = 30):
        self.cache_service = CacheAwareFearGreedService(cache_timeout_minutes)
    
    async def get_current_fear_greed_index(self) -> Optional[Dict]:
        """
        获取当前恐慌贪婪指数 - 兼容原DataFetcher接口
        
        Returns:
            与原DataFetcher相同格式的数据字典
        """
        return await self.cache_service.get_current_fear_greed_index()
    
    async def force_refresh(self) -> Optional[Dict]:
        """强制刷新数据"""
        return await self.cache_service.get_current_fear_greed_index(force_refresh=True)
    
    async def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return await self.cache_service.get_cache_status()


# 创建全局实例
_smart_fetcher_instance: Optional[SmartDataFetcher] = None


def get_smart_fetcher(cache_timeout_minutes: int = 30) -> SmartDataFetcher:
    """获取智能数据获取器实例"""
    global _smart_fetcher_instance
    
    if _smart_fetcher_instance is None:
        _smart_fetcher_instance = SmartDataFetcher(cache_timeout_minutes)
    
    return _smart_fetcher_instance


# 便捷函数
async def get_fear_greed_with_cache(cache_timeout_minutes: int = 30) -> Optional[Dict]:
    """便捷函数：获取恐慌贪婪指数（使用缓存）"""
    fetcher = get_smart_fetcher(cache_timeout_minutes)
    return await fetcher.get_current_fear_greed_index()


async def force_refresh_data() -> Optional[Dict]:
    """便捷函数：强制刷新数据"""
    fetcher = get_smart_fetcher()
    return await fetcher.force_refresh()


async def get_data_cache_status() -> Dict:
    """便捷函数：获取缓存状态"""
    fetcher = get_smart_fetcher()
    return await fetcher.get_cache_info()
