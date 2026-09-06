"""
Hint Policy Module - Phiên bản V1
Định nghĩa 4 cấp độ gợi ý sư phạm và kiểm soát việc tiết lộ giải pháp.
"""

PROMPT_VERSION = "v1"

HINT_LEVEL_POLICY_V1 = {
    1: {
        "name": "Socratic question",
        "description": "Đặt câu hỏi gợi mở định hướng tư duy, giúp học viên tự rà soát lại đoạn mã của mình mà không đưa ra câu trả lời.",
        "solution_allowed": False,
        "instruction": (
            "CẤP ĐỘ 1 (Mức 1 - Socratic question):\n"
            "- Đặt 1-2 câu hỏi gợi mở khéo léo để sinh viên tự quan sát và phát hiện ra vấn đề.\n"
            "- Không nêu ra lỗi cụ thể, không giải thích khái niệm sâu và TUYỆT ĐỐI KHÔNG cung cấp mã nguồn giải pháp.\n"
            "- 'solution_revealed' BẮT BUỘC là false."
        ),
    },
    2: {
        "name": "Conceptual explanation",
        "description": "Giải thích khái niệm OOP liên quan và manh mối logic mà không viết code sửa thay học viên.",
        "solution_allowed": False,
        "instruction": (
            "CẤP ĐỘ 2 (Mức 2 - Conceptual explanation):\n"
            "- Giải thích ngắn gọn, trực quan về nguyên lý OOP liên quan (ví dụ: cách constructor hoạt động, phạm vi của biến, từ khóa this).\n"
            "- Cung cấp manh mối logic về nguyên nhân vấn đề.\n"
            "- TUYỆT ĐỐI KHÔNG viết mã sửa lỗi thay cho sinh viên.\n"
            "- 'solution_revealed' BẮT BUỘC là false."
        ),
    },
    3: {
        "name": "Directed hint",
        "description": "Chỉ dẫn có mục tiêu từng bước khắc phục lỗi, nhưng vẫn để sinh viên tự viết mã sửa.",
        "solution_allowed": False,
        "instruction": (
            "CẤP ĐỘ 3 (Mức 3 - Directed hint):\n"
            "- Chỉ ra cụ thể dòng hoặc khối lệnh cần can thiệp.\n"
            "- Hướng dẫn từng bước sửa (scaffolding) để sinh viên tự gõ code hoàn thiện.\n"
            "- TUYỆT ĐỐI KHÔNG cung cấp toàn bộ đoạn code giải hoàn chỉnh.\n"
            "- 'solution_revealed' BẮT BUỘC là false."
        ),
    },
    4: {
        "name": "Explicit solution",
        "description": "Cung cấp giải pháp rõ ràng, giải thích cách sửa và cung cấp đoạn mã mẫu hoàn chỉnh.",
        "solution_allowed": True,
        "instruction": (
            "CẤP ĐỘ 4 (Mức 4 - Explicit solution):\n"
            "- Sinh viên đã yêu cầu xem giải pháp rõ ràng.\n"
            "- Cung cấp đoạn mã C# sửa đổi chuẩn mực kèm giải thích tường minh từng thay đổi.\n"
            "- 'solution_revealed' có thể là true."
        ),
    },
}


def get_hint_instruction(hint_level: int) -> str:
    """Trả về chỉ dẫn gợi ý tương ứng với cấp độ cấu hình (1..4)."""
    policy = HINT_LEVEL_POLICY_V1.get(hint_level, HINT_LEVEL_POLICY_V1[1])
    return policy["instruction"]


def is_solution_allowed(hint_level: int) -> bool:
    """Xác định liệu cấp độ gợi ý này có cho phép lộ giải pháp hoàn chỉnh hay không."""
    policy = HINT_LEVEL_POLICY_V1.get(hint_level, HINT_LEVEL_POLICY_V1[1])
    return policy["solution_allowed"]
