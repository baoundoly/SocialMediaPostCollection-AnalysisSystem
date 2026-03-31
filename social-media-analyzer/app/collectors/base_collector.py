import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.models.source_config import SourceConfig
from app.core.security import decrypt_value

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    def __init__(self, source_config: SourceConfig):
        self.source_config = source_config
        self.api_key = self._decrypt_optional(source_config.api_key_encrypted)
        self.access_token = self._decrypt_optional(source_config.access_token_encrypted)
        self.demo_mode = not (self.api_key or self.access_token)

    def _decrypt_optional(self, value):
        if not value: return None
        try: return decrypt_value(value)
        except Exception: return None

    @abstractmethod
    def fetch_posts(self) -> List[Dict[str, Any]]: pass

    def _retry(self, func, *args, **kwargs):
        for attempt in range(self.MAX_RETRIES):
            try: return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1: time.sleep(self.RETRY_DELAY * (attempt + 1))
        raise RuntimeError(f"All {self.MAX_RETRIES} attempts failed")

    def _demo_posts(self, platform_name):
        from datetime import datetime, timedelta
        import random, uuid
        contents = [
            f"Amazing new features in {platform_name}! #tech #innovation",
            f"Breaking news: Major developments in the industry. #news",
            f"Just tried the new product - absolutely love it! #review",
            f"Feeling inspired today. Keep pushing forward! #motivation",
            f"The economy is showing signs of recovery. #economy",
            f"Exciting announcement coming soon! #announcement",
            f"This is terrible. I cannot believe this happened. #upset",
            f"Beautiful weather today. Perfect for outdoor activities! #outdoors",
            f"New research shows promising results in renewable energy. #sustainability",
            f"Join us for our upcoming event. Limited seats available! #event",
        ]
        now = datetime.utcnow()
        return [{
            "external_post_id": str(uuid.uuid4()), "author_name": f"Demo User {i+1}",
            "author_handle": f"@demouser{i+1}", "content": contents[i % len(contents)],
            "post_url": f"https://{platform_name.lower()}.com/post/{i+1}", "media_url": None,
            "posted_at": now - timedelta(hours=random.randint(1, 72)),
            "likes_count": random.randint(0, 10000), "comments_count": random.randint(0, 500),
            "shares_count": random.randint(0, 1000), "views_count": random.randint(0, 100000),
            "raw_payload": None,
        } for i in range(10)]
