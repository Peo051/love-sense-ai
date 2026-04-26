from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.inference.emotion_predictor import EmotionPredictor
from app.inference.reply_generator import ReplyGenerator
from app.preprocessing.vietnamese_normalizer import VietnameseNormalizer
from app.safety.output_validator import OutputValidator

app = FastAPI(
    title="Love Emotion AI Service",
    description="AI service for emotion analysis",
    version="1.0.0"
)

# Initialize models
emotion_predictor = EmotionPredictor()
reply_generator = ReplyGenerator()
normalizer = VietnameseNormalizer()
validator = OutputValidator()

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    emotion: str
    confidence: float
    emotions: list
    suggested_replies: list

@app.get("/")
async def root():
    return {"message": "Love Emotion AI Service"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    try:
        # Normalize text
        normalized_text = normalizer.normalize(request.text)
        
        # Predict emotion
        emotion_result = emotion_predictor.predict(normalized_text)
        
        # Generate replies
        replies = reply_generator.generate(normalized_text, emotion_result["emotion"])
        
        # Validate output
        if not validator.is_safe(replies):
            replies = ["Cảm ơn bạn!", "Rất vui được nói chuyện!"]
        
        return PredictResponse(
            emotion=emotion_result["emotion"],
            confidence=emotion_result["confidence"],
            emotions=emotion_result["emotions"],
            suggested_replies=replies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
