import numpy as np
from typing import Dict, List

class EmotionPredictor:
    def __init__(self):
        self.emotions = [
            "Hạnh phúc",
            "Yêu thương", 
            "Quan tâm",
            "Buồn",
            "Lo lắng",
            "Giận dữ"
        ]
        # TODO: Load actual model
        
    def predict(self, text: str) -> Dict:
        """Predict emotion from text"""
        # TODO: Replace with actual model inference
        # This is a placeholder implementation
        
        # Simple keyword-based prediction for demo
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["yêu", "thương", "love"]):
            primary_emotion = "Yêu thương"
            confidence = 0.85
        elif any(word in text_lower for word in ["vui", "hạnh phúc", "happy"]):
            primary_emotion = "Hạnh phúc"
            confidence = 0.80
        elif any(word in text_lower for word in ["buồn", "sad"]):
            primary_emotion = "Buồn"
            confidence = 0.75
        else:
            primary_emotion = "Quan tâm"
            confidence = 0.70
        
        # Generate emotion scores
        emotions = self._generate_emotion_scores(primary_emotion)
        
        return {
            "emotion": primary_emotion,
            "confidence": confidence,
            "emotions": emotions
        }
    
    def _generate_emotion_scores(self, primary: str) -> List[Dict]:
        """Generate scores for all emotions"""
        scores = []
        for emotion in self.emotions:
            if emotion == primary:
                value = np.random.uniform(0.7, 0.9)
            else:
                value = np.random.uniform(0.1, 0.5)
            scores.append({"name": emotion, "value": round(value, 2)})
        
        # Sort by value
        scores.sort(key=lambda x: x["value"], reverse=True)
        return scores[:3]  # Return top 3
