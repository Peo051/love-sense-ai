# Love Emotion Web - Project Guide

## Mục tiêu MVP

MVP tập trung vào luồng chính:

Người dùng nhập đoạn chat và bối cảnh cá nhân hóa → frontend gửi `POST /api/analyze` → backend validate dữ liệu → mock AI service trả JSON → frontend hiển thị kết quả.

## Nguyên tắc an toàn

- Không đọc trộm Zalo, Messenger, SMS, thông báo hoặc danh bạ.
- Không kết luận chắc chắn cảm xúc, hành vi hoặc lòng chung thủy của người khác.
- Không đưa lời khuyên thao túng cảm xúc.
- Không lưu nội dung chat mặc định.
- Luôn hiển thị cảnh báo: “Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.”

## Phần chính

- `backend/app/routes/analyze.py`: endpoint phân tích.
- `backend/app/schemas/analyze_schema.py`: request/response contract.
- `backend/app/services/ai_service.py`: mock analysis logic cho MVP.
- `frontend/app/analyze/page.tsx`: orchestration state và API call.
- `frontend/components/analyze/AnalysisForm.tsx`: form nhập chat/context.
- `frontend/components/analyze/AnalysisResultPanel.tsx`: hiển thị kết quả.

## Chưa có trong MVP

- Đăng nhập.
- Database thật.
- Lưu lịch sử phân tích.
- LLM API thật.
- Fine-tune model.
- Deploy production.
