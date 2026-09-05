"""
Diagnosis Prompt Module - Phiên bản V1
Yêu cầu mô hình thực hiện chẩn đoán lỗi kỹ thuật và ngộ nhận có cấu trúc.
"""

PROMPT_VERSION = "v1"

DIAGNOSIS_SCHEMA_PROMPT_V1 = """=== QUY TẮC CHẨN ĐOÁN KỸ THUẬT CÓ CẤU TRÚC (DIAGNOSIS V1) ===

Bạn PHẢI thực hiện phân tích có cấu trúc dựa trên bằng chứng mã nguồn sinh viên:
1. Diagnosis:
   - issue_type: phân loại lỗi chính xác ('syntax_error', 'semantic_error', 'logical_error', 'conceptual_misconception', 'oop_design_flaw', hoặc 'none').
   - severity: 'info', 'warning', hoặc 'error'.
   - location: vị trí lỗi cụ thể (dòng code, tên class, hoặc phương thức).
   - confidence: độ tin cậy của chẩn đoán (0.0 đến 1.0). Nếu thiếu bằng chứng, confidence phải <= 0.6.
2. knowledge_components (Knowledge Components):
   - Danh sách các khái niệm OOP liên quan (ví dụ: 'class_constructor', 'encapsulation', 'this_keyword', 'member_access', 'inheritance').
3. possible_misconception:
   - type: mã nhận diện ngộ nhận (ví dụ: 'constructor_parameter_shadowing', 'static_vs_instance_confusion').
   - description: giải thích giả thuyết ngộ nhận theo ngôn ngữ giả định.
   - confidence: độ tin cậy của giả thuyết ngộ nhận (0.0 đến 1.0).
4. evidence:
   - code: trích xuất chính xác đoạn mã làm bằng chứng từ <untrusted_student_code>.
   - reason: lý giải vì sao đoạn mã này thể hiện vấn đề hoặc ngộ nhận.

OUTPUT BẮT BUỘC:
Đầu ra chẩn đoán phải được trả về dưới dạng JSON có cấu trúc, KHÔNG đưa văn bản tự do ngoài JSON.
"""
