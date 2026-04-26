import re


class SafetyFilter:
    UNSAFE_PATTERNS = [
        r"\b(violence|hate|abuse)\b",
        r"(đọc\s*trộm|hack|theo\s*dõi\s*zalo|theo\s*dõi\s*messenger|nghe\s*lén)",
        r"(ép\s*buộc|thao\s*túng|đe\s*dọa|kiểm\s*soát)",
    ]

    @staticmethod
    def is_safe(text: str) -> bool:
        """Chặn các yêu cầu có dấu hiệu theo dõi, thao túng hoặc gây hại."""
        text_lower = text.lower()

        for pattern in SafetyFilter.UNSAFE_PATTERNS:
            if re.search(pattern, text_lower):
                return False

        return True

    @staticmethod
    def filter_text(text: str) -> str:
        """MVP không biến đổi nội dung chat; chỉ phân tích khi đã qua kiểm tra an toàn."""
        return text
