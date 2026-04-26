import re

class VietnameseNormalizer:
    def __init__(self):
        # Common Vietnamese text variations
        self.replacements = {
            "ko": "không",
            "k": "không",
            "dc": "được",
            "đc": "được",
            "vs": "với",
            "nx": "nữa",
            "j": "gì",
            "mk": "mình",
            "t": "tôi",
            "m": "mày",
            "iu": "yêu",
            "ik": "đi",
            "r": "rồi",
            "hok": "không",
            "bik": "biết",
            "lm": "làm"
        }
    
    def normalize(self, text: str) -> str:
        """Normalize Vietnamese text"""
        # Convert to lowercase for processing
        text_lower = text.lower()
        
        # Replace teencode
        words = text_lower.split()
        normalized_words = []
        
        for word in words:
            if word in self.replacements:
                normalized_words.append(self.replacements[word])
            else:
                normalized_words.append(word)
        
        normalized = " ".join(normalized_words)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
