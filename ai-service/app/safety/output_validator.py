import re
from typing import List

class OutputValidator:
    def __init__(self):
        self.unsafe_patterns = [
            r'\b(violence|kill|hurt|harm)\b',
            r'\b(hate|racist|discrimination)\b',
            # Add more patterns
        ]
        
        self.unsafe_keywords = [
            "bạo lực", "giết", "đánh", "hại",
            "ghét", "phân biệt"
        ]
    
    def is_safe(self, replies: List[str]) -> bool:
        """Validate if replies are safe"""
        for reply in replies:
            if not self._check_single_reply(reply):
                return False
        return True
    
    def _check_single_reply(self, reply: str) -> bool:
        """Check if a single reply is safe"""
        reply_lower = reply.lower()
        
        # Check patterns
        for pattern in self.unsafe_patterns:
            if re.search(pattern, reply_lower):
                return False
        
        # Check keywords
        for keyword in self.unsafe_keywords:
            if keyword in reply_lower:
                return False
        
        return True
    
    def filter_unsafe_content(self, text: str) -> str:
        """Filter out unsafe content"""
        # Implement filtering logic
        return text
