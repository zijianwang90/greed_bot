"""
Mock data fetcher for testing
Returns simulated Fear & Greed Index data
"""

import random
from datetime import datetime
from typing import Dict, Optional

class MockDataFetcher:
    """Mock data fetcher that returns simulated data"""
    
    async def get_current_fear_greed_index(self) -> Optional[Dict]:
        """Return mock Fear & Greed Index data"""
        # Generate a random value between 0-100
        value = random.randint(20, 80)
        
        # Determine rating based on value
        if value <= 24:
            rating = "Extreme Fear"
        elif value <= 49:
            rating = "Fear"
        elif value == 50:
            rating = "Neutral"
        elif value <= 74:
            rating = "Greed"
        else:
            rating = "Extreme Greed"
        
        return {
            'score': value,
            'rating': rating,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'previous_close': value - random.randint(-5, 5),
            'week_ago': value - random.randint(-10, 10),
            'month_ago': value - random.randint(-20, 20),
            'year_ago': value - random.randint(-30, 30),
            'source': 'Mock Data (Testing)'
        }
    
    async def get_vix_data(self) -> Optional[Dict]:
        """Return mock VIX data"""
        value = round(random.uniform(12, 35), 2)
        previous = round(value - random.uniform(-2, 2), 2)
        change = round(value - previous, 2)
        change_percent = round((change / previous) * 100, 2) if previous else 0
        
        return {
            'value': value,
            'previous_close': previous,
            'change': change,
            'change_percent': change_percent
        }
    
    async def get_historical_data(self, days: int = 30) -> list:
        """Return mock historical data"""
        data = []
        current_value = random.randint(30, 70)
        
        for i in range(days):
            value = current_value + random.randint(-5, 5)
            value = max(0, min(100, value))  # Keep within 0-100 range
            
            data.append({
                'date': f"Day {i+1}",
                'value': value,
                'rating': self._get_rating(value)
            })
            
            current_value = value
        
        return data
    
    def _get_rating(self, value: int) -> str:
        """Get rating from value"""
        if value <= 24:
            return "Extreme Fear"
        elif value <= 49:
            return "Fear"
        elif value == 50:
            return "Neutral"
        elif value <= 74:
            return "Greed"
        else:
            return "Extreme Greed" 