from typing import List, Dict, Any
from app.collectors.base_collector import BaseCollector

class YouTubeCollector(BaseCollector):
    PLATFORM_NAME = "Youtube"

    def fetch_posts(self) -> List[Dict[str, Any]]:
        if self.demo_mode:
            return self._demo_posts(self.PLATFORM_NAME)
        return self._retry(self._fetch_real_posts)

    def _fetch_real_posts(self) -> List[Dict[str, Any]]:
        return self._demo_posts(self.PLATFORM_NAME)
