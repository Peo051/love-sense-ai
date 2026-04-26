from typing import List

class UnsafeAdviceFilter:
    def __init__(self):
        self.unsafe_advice_patterns = [
            "break up",
            "chia tay",
            "bỏ nhau",
            "đừng yêu nữa",
            "hết tình cảm"
        ]
    
    def filter(self, advice_list: List[str]) -> List[str]:
        """Filter out unsafe advice"""
        safe_advice = []
        
        for advice in advice_list:
            if self._is_safe_advice(advice):
                safe_advice.append(advice)
        
        return safe_advice
    
    def _is_safe_advice(self, advice: str) -> bool:
        """Check if advice is safe"""
        advice_lower = advice.lower()
        
        for pattern in self.unsafe_advice_patterns:
            if pattern in advice_lower:
                return False
        
        return True
