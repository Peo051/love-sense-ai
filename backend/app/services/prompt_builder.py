from typing import Optional

class PromptBuilder:
    @staticmethod
    def build_emotion_prompt(
        text: str,
        user_context: Optional[dict] = None
    ) -> str:
        """Build prompt for emotion analysis"""
        prompt = f"Phân tích cảm xúc của tin nhắn sau:\n\n{text}\n\n"
        
        if user_context:
            prompt += "Thông tin người dùng:\n"
            if "communication_style" in user_context:
                prompt += f"- Phong cách giao tiếp: {user_context['communication_style']}\n"
        
        prompt += "\nTrả về cảm xúc chính và độ tin cậy."
        return prompt
