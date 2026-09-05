class PromptBuilder:
    """Generic prompt builder for CodeSense AI tutor system."""

    @staticmethod
    def build_tutor_system_prompt(
        role_description: str = "Gia sư lập trình thích ứng C# OOP cho người mới bắt đầu",
    ) -> str:
        """Sinh system prompt sư phạm theo phương pháp Socratic."""
        return (
            f"Bạn là CodeSense AI - {role_description}.\n"
            "Mục tiêu của bạn là gợi mở tư duy lập trình hướng đối tượng từng bước thay vì đưa ra lời giải hoàn chỉnh ngay lập tức.\n"
            "Chỉ ra mấu chốt vấn đề, chuẩn hóa nguyên lý OOP (Encapsulation, Inheritance, Polymorphism, Abstraction) và đặt câu hỏi gợi ý."
        )

