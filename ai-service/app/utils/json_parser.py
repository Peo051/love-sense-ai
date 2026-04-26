import json
import re
from typing import Any, Dict

class JSONParser:
    @staticmethod
    def parse(text: str) -> Dict:
        """Parse JSON from text"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            return JSONParser.extract_json(text)
    
    @staticmethod
    def extract_json(text: str) -> Dict:
        """Extract JSON from text that may contain other content"""
        # Find JSON-like patterns
        json_pattern = r'\{[^{}]*\}'
        matches = re.findall(json_pattern, text)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        return {}
    
    @staticmethod
    def safe_parse(text: str, default: Any = None) -> Any:
        """Safely parse JSON with default fallback"""
        try:
            return json.loads(text)
        except:
            return default
