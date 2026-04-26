from app.schemas.analyze_schema import AnalyzeResponse


WARNING_MESSAGE = "Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp."


class AIService:
    async def analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        """Sinh kết quả mock cho MVP, chưa gọi LLM thật để tránh phụ thuộc API key."""
        text_lower = chat_text.lower()
        context_lower = profile_context.lower()

        fatigue_keywords = ["mệt", "không sao", "lạ", "im", "nghỉ", "đuối"]
        sadness_keywords = ["buồn", "tủi", "khóc", "cô đơn", "thất vọng"]
        conflict_keywords = ["giận", "bực", "khó chịu", "đừng hỏi", "không muốn nói"]
        affection_keywords = ["yêu", "nhớ", "thương", "vui", "hạnh phúc"]

        fatigue_score = self._keyword_score(text_lower, fatigue_keywords)
        sadness_score = self._keyword_score(text_lower, sadness_keywords)
        conflict_score = self._keyword_score(text_lower, conflict_keywords)
        affection_score = self._keyword_score(text_lower, affection_keywords)

        if fatigue_score or "không sao" in text_lower:
            return self._fatigue_response(profile_context, context_lower)

        if conflict_score:
            return AnalyzeResponse(
                overall_emotion="căng thẳng / cần khoảng lặng",
                confidence=0.68,
                emotion_distribution={
                    "căng_thẳng": 0.34,
                    "né_tránh": 0.24,
                    "buồn": 0.18,
                    "trung_lập": 0.24,
                },
                summary=(
                    "Đoạn chat có thể đang có căng thẳng hoặc người kia chưa sẵn sàng trao đổi. "
                    "Không đủ dữ liệu để kết luận chắc chắn nguyên nhân hay cảm xúc thật sự."
                ),
                context_note=self._build_context_note(profile_context, context_lower),
                suggested_reply=(
                    "Anh hiểu là lúc này em có thể chưa muốn nói nhiều. "
                    "Mình nghỉ một chút, khi nào em sẵn sàng thì anh nghe em chia sẻ nhé."
                ),
                warning=WARNING_MESSAGE,
            )

        if sadness_score:
            return AnalyzeResponse(
                overall_emotion="buồn / cần được lắng nghe",
                confidence=0.7,
                emotion_distribution={
                    "buồn": 0.36,
                    "mệt_mỏi": 0.22,
                    "lo_lắng": 0.18,
                    "trung_lập": 0.24,
                },
                summary=(
                    "Đoạn chat có thể cho thấy người kia đang buồn hoặc cần được lắng nghe nhẹ nhàng. "
                    "Nên tránh suy diễn quá xa khi chưa có thêm ngữ cảnh."
                ),
                context_note=self._build_context_note(profile_context, context_lower),
                suggested_reply=(
                    "Anh ở đây nghe em mà. Nếu em muốn kể thì cứ nói từ từ, "
                    "còn nếu em cần yên tĩnh một chút anh cũng tôn trọng."
                ),
                warning=WARNING_MESSAGE,
            )

        if affection_score:
            return AnalyzeResponse(
                overall_emotion="ấm áp / tích cực",
                confidence=0.74,
                emotion_distribution={
                    "yêu_thương": 0.38,
                    "vui_vẻ": 0.28,
                    "quan_tâm": 0.18,
                    "trung_lập": 0.16,
                },
                summary=(
                    "Đoạn chat có nhiều tín hiệu tích cực và gần gũi. "
                    "Dù vậy, kết quả vẫn chỉ là nhận định tham khảo từ ngôn từ trong hội thoại."
                ),
                context_note=self._build_context_note(profile_context, context_lower),
                suggested_reply=(
                    "Anh cũng rất vui khi nghe em nói vậy. "
                    "Mình cứ nói chuyện nhẹ nhàng và thật lòng với nhau nha."
                ),
                warning=WARNING_MESSAGE,
            )

        return AnalyzeResponse(
            overall_emotion="trung lập / chưa đủ dữ liệu",
            confidence=0.56,
            emotion_distribution={
                "trung_lập": 0.42,
                "lo_lắng": 0.2,
                "mệt_mỏi": 0.18,
                "quan_tâm": 0.2,
            },
            summary=(
                "Đoạn chat chưa có đủ dấu hiệu rõ ràng để phân loại cảm xúc mạnh. "
                "Nên hỏi thăm trực tiếp và tôn trọng nhịp phản hồi của người kia."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply=(
                "Anh chưa chắc mình hiểu đúng cảm xúc của em. "
                "Nếu em muốn, mình nói chuyện thêm một chút để anh hiểu em hơn nhé."
            ),
            warning=WARNING_MESSAGE,
        )

    def _fatigue_response(self, profile_context: str, context_lower: str) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="mệt mỏi / né tránh nhẹ",
            confidence=0.72,
            emotion_distribution={
                "mệt_mỏi": 0.35,
                "né_tránh": 0.25,
                "buồn": 0.20,
                "trung_lập": 0.20,
            },
            summary=(
                "Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều. "
                "Không đủ dữ liệu để kết luận chắc chắn cảm xúc thật sự."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply=(
                "Anh hiểu rồi, em nghỉ một chút nha. "
                "Khi nào em muốn nói thì anh vẫn ở đây nghe em."
            ),
            warning=WARNING_MESSAGE,
        )

    def _build_context_note(self, profile_context: str, context_lower: str) -> str:
        if not profile_context.strip():
            return "Bạn chưa nhập nhiều bối cảnh cá nhân hóa, nên kết quả chỉ dựa trên nội dung chat."

        if "im lặng" in context_lower or "hỏi dồn" in context_lower:
            return "Nếu người này thường im lặng khi mệt, nên phản hồi nhẹ nhàng thay vì hỏi dồn."

        if "không thích" in context_lower or "cần không gian" in context_lower:
            return "Bối cảnh cá nhân hóa cho thấy nên tôn trọng không gian riêng và tránh tạo áp lực."

        return (
            "Bối cảnh cá nhân hóa đã được dùng để điều chỉnh gợi ý, "
            "nhưng không thể thay thế việc hỏi thăm trực tiếp."
        )

    def _keyword_score(self, text: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)
