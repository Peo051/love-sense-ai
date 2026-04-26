from typing import Dict

class SentimentPredictor:
    def __init__(self):
        # TODO: Load sentiment model
        pass
    
    def predict(self, text: str) -> Dict:
        """Predict sentiment (positive/negative/neutral)"""
        # TODO: Implement actual sentiment prediction
        
        # Placeholder implementation
        text_lower = text.lower()
        
        positive_words = ["yêu", "thích", "vui", "hạnh phúc", "tuyệt"]
        negative_words = ["buồn", "tệ", "ghét", "giận"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.8
        elif neg_count > pos_count:
            sentiment = "negative"
            score = 0.7
        else:
            sentiment = "neutral"
            score = 0.6
        
        return {
            "sentiment": sentiment,
            "score": score
        }
