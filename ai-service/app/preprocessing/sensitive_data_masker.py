import re

class SensitiveDataMasker:
    def __init__(self):
        self.patterns = {
            "phone": r'\b\d{10,11}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "address": r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd)',
        }
    
    def mask(self, text: str) -> str:
        """Mask sensitive data in text"""
        masked_text = text
        
        # Mask phone numbers
        masked_text = re.sub(self.patterns["phone"], "[PHONE]", masked_text)
        
        # Mask emails
        masked_text = re.sub(self.patterns["email"], "[EMAIL]", masked_text)
        
        # Mask URLs
        masked_text = re.sub(self.patterns["url"], "[URL]", masked_text)
        
        return masked_text
    
    def has_sensitive_data(self, text: str) -> bool:
        """Check if text contains sensitive data"""
        for pattern in self.patterns.values():
            if re.search(pattern, text):
                return True
        return False
