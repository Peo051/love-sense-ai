"""
Diagnosis Prompt Module - Phiên bản V1
Yêu cầu mô hình thực hiện chẩn đoán lỗi kỹ thuật và ngộ nhận có cấu trúc.
"""

PROMPT_VERSION = "v1"

DIAGNOSIS_SCHEMA_PROMPT_V1 = """=== QUY TẮC CHẨN ĐOÁN KỸ THUẬT CÓ CẤU TRÚC (DIAGNOSIS V1) ===

Bạn PHẢI thực hiện phân tích có cấu trúc dựa trên bằng chứng mã nguồn sinh viên:
1. Diagnosis:
   - category: bắt buộc là một trong 8 phân loại chuẩn sau:
     * 'compile_error': Lỗi biên dịch cú pháp hoặc kiểu (syntax_error, type_mismatch, missing_semicolon, v.v.)
     * 'runtime_error': Lỗi thực thi (recursive_property_accessor, null_reference_risk, index_out_of_range, v.v.)
     * 'logic_error': Sai sót logic (parameter_field_shadowing, invalid_setter_validation, incorrect_calculation, v.v.)
     * 'conceptual_misuse': Dùng sai khái niệm OOP (static_instance_confusion, encapsulation_bypass, constructor_return_type, v.v.)
     * 'requirement_violation': Vi phạm yêu cầu đề bài (missing_required_member, incorrect_signature, v.v.)
     * 'no_bug': Mã nguồn đúng và đạt chuẩn OOP. BẮT BUỘC KHÔNG ĐƯỢC BỊA ĐẶT LỖI!
     * 'insufficient_context': Mã nguồn nộp vào chưa hoàn chỉnh hoặc quá ngắn để kết luận.
     * 'unknown': Chưa xác định rõ ràng.
   - issue_type: tên lỗi cụ thể theo taxonomy chuẩn. Nếu là 'no_bug', ghi 'no_issue_detected'.
   - severity: 'info', 'warning', hoặc 'error' (nếu 'no_bug' bắt buộc là 'info').
   - location: vị trí lỗi cụ thể (dòng code, tên class, hoặc phương thức).
   - confidence: độ tin cậy của chẩn đoán (0.0 đến 1.0). Nếu thiếu bằng chứng, confidence phải <= 0.6.
2. knowledge_components (Knowledge Components):
   - Danh sách các khái niệm OOP liên quan (ví dụ: 'csharp_constructor', 'encapsulation', 'this_keyword', 'member_access', 'inheritance').
3. possible_misconception:
   - Nếu category là 'no_bug' hoặc 'insufficient_context', trường này BẮT BUỘC LÀ null!
   - Nếu có lỗi:
     * type: mã nhận diện ngộ nhận (ví dụ: 'parameter_shadowing_confusion', 'static_vs_instance_scope_confusion').
     * description: giải thích giả thuyết ngộ nhận theo ngôn ngữ giả định.
     * confidence: độ tin cậy của giả thuyết ngộ nhận (0.0 đến 1.0).
4. evidence:
   - code: trích xuất chính xác đoạn mã làm bằng chứng từ <untrusted_student_code>.
   - reason: lý giải vì sao đoạn mã này thể hiện vấn đề hoặc ngộ nhận.

QUY TẮC CỐT LÕI:
- Không bắt buộc mọi bài nộp đều phải có lỗi. Nếu sinh viên làm đúng, hãy công nhận và hướng dẫn mở rộng nâng cao.
- OUTPUT BẮT BUỘC: Đầu ra chẩn đoán phải được trả về dưới dạng JSON có cấu trúc, KHÔNG đưa văn bản tự do ngoài JSON.
"""
