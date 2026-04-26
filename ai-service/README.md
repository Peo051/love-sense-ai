# Love Emotion AI Service

AI service phân tích cảm xúc trong tin nhắn tình yêu.

## Tính năng

- Phân tích cảm xúc từ văn bản tiếng Việt
- Xử lý teencode và emoji
- Đề xuất câu trả lời phù hợp
- Lọc nội dung không an toàn
- Che giấu thông tin nhạy cảm

## Cài đặt

```bash
cd ai-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Chạy service

```bash
uvicorn app.main:app --reload --port 8001
```

API sẽ chạy tại http://localhost:8001

## API Endpoints

### POST /predict
Phân tích cảm xúc từ văn bản

Request:
```json
{
  "text": "Em yêu anh!"
}
```

Response:
```json
{
  "emotion": "Yêu thương",
  "confidence": 0.85,
  "emotions": [
    {"name": "Yêu thương", "value": 0.85},
    {"name": "Hạnh phúc", "value": 0.70}
  ],
  "suggested_replies": [
    "Anh cũng yêu em!",
    "Em là tất cả của anh!"
  ]
}
```

## Training

### Chuẩn bị dữ liệu
```bash
python training/scripts/prepare_dataset.py
```

### Huấn luyện model
```bash
python training/scripts/train_model.py
```

### Đánh giá model
```bash
python training/scripts/evaluate_model.py
```

### Export model
```bash
python training/scripts/export_model.py
```

## Cấu trúc

- `app/inference/` - Các module inference
- `app/preprocessing/` - Xử lý văn bản
- `app/safety/` - Kiểm tra an toàn
- `training/` - Scripts và notebooks training
- `models/` - Lưu trữ models
