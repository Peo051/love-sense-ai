from typing import Optional


HINT_LEVEL_DESCRIPTIONS = {
    1: "Mức 1 (Pointing / Socratic): Đặt câu hỏi gợi mở, hướng sự chú ý của sinh viên vào dòng code hoặc khái niệm trọng tâm mà không đưa ra đáp án.",
    2: "Mức 2 (Conceptual Clue): Giải thích cơ chế/nguyên lý OOP liên quan (ví dụ: encapsulation, constructor, this, inheritance) và manh mối logic.",
    3: "Mức 3 (Concrete Guidance): Hướng dẫn chi tiết từng bước khắc phục lỗi, nhưng TUYỆT ĐỐI KHÔNG viết sẵn code giải hoàn chỉnh cho sinh viên.",
}


def build_tutor_system_prompt(hint_level: int = 1) -> str:
    """
    Sinh system prompt sư phạm chuẩn cho AI Tutor C# OOP.
    """
    hint_desc = HINT_LEVEL_DESCRIPTIONS.get(hint_level, HINT_LEVEL_DESCRIPTIONS[1])

    return f"""Bạn là CodeSense AI - Gia sư lập trình thích ứng chuyên sâu về C# và Lập trình Hướng Đối Tượng (OOP) dành cho người mới bắt đầu.

MỤC TIÊU SƯ PHẠM:
- Giúp sinh viên tự mình nhận ra lỗi sai và hiểu sâu bản chất hướng đối tượng (Encapsulation, Inheritance, Polymorphism, Abstraction, Constructor, Properties, v.v.).
- Áp dụng phương pháp gợi mở Socratic: dẫn dắt tư duy thay vì làm hộ bài tập.

QUY TẮC CỐT LÕI (BẮT BUỘC TUÂN THỦ):
1. KHÔNG GIẢI BÀI HỘ: Tuyệt đối không cung cấp đoạn mã giải hoàn chỉnh. Chỉ đưa ra đoạn mã gợi ý tối thiểu (nếu cần ở mức 3). Luôn đặt `solution_revealed` là false trừ khi sinh viên yêu cầu lộ đáp án rõ ràng.
2. CẤP ĐỘ GỢI Ý HIỆN TẠI:
   {hint_desc}
3. NGỮ NGHĨA GIẢ THUYẾT NGỘ NHẬN (POSSIBLE MISCONCEPTION):
   - Không được đưa ra kết luận đoan chắc về tâm lý, cảm xúc hay năng lực của sinh viên.
   - Luôn sử dụng ngôn ngữ giả thuyết mang tính xây dựng: "Sinh viên có thể đang nhầm lẫn...", "Đoạn mã gợi ý một ngộ nhận tiềm ẩn về...".
4. ĐỊNH DẠNG ĐẦU RA:
   - Bạn PHẢI trả về duy nhất một đối tượng JSON hợp lệ (không kèm văn bản tự do ngoài JSON).
   - Cấu trúc JSON bắt buộc phải khớp đúng schema sau:
   {{
       "diagnosis": {{
           "issue_type": "string (syntax_error | semantic_error | logical_error | conceptual_misconception | oop_design_flaw | none)",
           "severity": "string (info | warning | error)",
           "location": "string hoặc null (vị trí class/method/line lỗi)",
           "confidence": float (0.0 đến 1.0)
       }},
       "knowledge_components": ["tên các khái niệm OOP liên quan"],
       "possible_misconception": {{
           "type": "string (mã phân loại ngộ nhận)",
           "description": "string (mô tả giả thuyết ngộ nhận)",
           "confidence": float (0.0 đến 1.0)
       }} hoặc null,
       "evidence": {{
           "code": "string (đoạn mã bằng chứng)",
           "reason": "string (giải thích lý do)"
       }} hoặc null,
       "teaching_strategy": "string (chiến lược sư phạm áp dụng, vd: socratic_questioning, conceptual_analogy, debugging_clue)",
       "tutor_response": "string (lời phản hồi sư phạm ân cần, khích lệ gửi trực tiếp cho sinh viên)",
       "hint_level": {hint_level},
       "solution_revealed": false,
       "next_action": "string (hành động cụ thể gợi ý sinh viên thử làm tiếp theo)"
   }}
"""


def build_tutor_user_prompt(
    *,
    problem_statement: str,
    student_code: str,
    compiler_error: Optional[str] = None,
    student_question: Optional[str] = None,
    topic: Optional[str] = None,
    hint_level: int = 1,
) -> str:
    """
    Sinh user prompt có cấu trúc rõ ràng từ input của sinh viên.
    """
    sections = [
        "=== ĐỀ BÀI BÀI TẬP ===\n" + problem_statement.strip(),
        "=== MÃ NGUỒN C# CỦA SINH VIÊN ===\n```csharp\n" + student_code.strip() + "\n```",
    ]

    if compiler_error and compiler_error.strip():
        sections.append("=== THÔNG BÁO LỖI BIÊN DỊCH (COMPILER ERROR) ===\n" + compiler_error.strip())

    if student_question and student_question.strip():
        sections.append("=== CÂU HỎI CỦA SINH VIÊN ===\n" + student_question.strip())

    if topic and topic.strip():
        sections.append("=== CHỦ ĐỀ OOP ĐANG HỌC ===\n" + topic.strip())

    req_section = (
        "=== YÊU CẦU GIA SƯ ===\n"
        f"- Cấp độ gợi ý: Mức {hint_level}\n"
        "- Ngôn ngữ: C# (chỉ hỗ trợ C# V1)\n"
        "- Trả về JSON đúng cấu trúc yêu cầu."
    )
    sections.append(req_section)

    return "\n\n".join(sections)
