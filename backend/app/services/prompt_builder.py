from typing import Optional


class PromptBuilder:
    @staticmethod
    def build_emotion_prompt(text: str, user_context: Optional[dict] = None) -> str:
        """Build prompt for emotion analysis in a privacy-first, evidence-based format."""
        prompt = (
            "Phân tích sắc thái hội thoại sau theo hướng thận trọng và an toàn.\n"
            "Không kết luận chắc chắn cảm xúc hoặc ý định của người khác.\n"
            "Nếu có dấu hiệu thân mật, trêu đùa hoặc quan tâm rõ ràng, hãy phản ánh sắc thái đó.\n"
            "Phân biệt trung lập thật với thiếu dữ liệu.\n"
            "Nếu dữ liệu thiếu hoặc có thể đến từ OCR, giảm confidence và nêu điểm cần thận trọng.\n\n"
            f"Đoạn chat:\n{text}\n\n"
        )

        if user_context:
            prompt += "Bối cảnh cá nhân hóa:\n"
            if "communication_style" in user_context:
                prompt += f"- Phong cách giao tiếp: {user_context['communication_style']}\n"
            if "input_source" in user_context:
                prompt += f"- Nguồn dữ liệu: {user_context['input_source']}\n"

        prompt += (
            "\nTrả về JSON có overall_emotion, confidence, emotion_distribution, summary, "
            "context_note, suggested_reply, warning, tone, evidence dạng {quote,label,reason}, "
            "uncertainty_reasons, input_quality và reply_style."
        )
        return prompt
