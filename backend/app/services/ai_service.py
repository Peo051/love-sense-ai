import unicodedata

from app.core.config import settings
from app.schemas.analyze_schema import AnalyzeResponse, EvidenceItem
from app.services.analysis_output_validator import validate_analysis_output
from app.services.analysis_policy import WARNING_MESSAGE
from app.services.llm_client import LLMClientError, OpenAICompatibleLLMClient


class AIService:
    def __init__(self, llm_client: OpenAICompatibleLLMClient | None = None):
        self.llm_client = llm_client or OpenAICompatibleLLMClient()

    async def analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        if self._should_use_mock():
            result = self._mock_analyze_emotion(chat_text, profile_context)
            return validate_analysis_output(result, chat_text, profile_context)

        try:
            result = await self.llm_client.analyze_emotion(chat_text, profile_context)
        except LLMClientError:
            result = self._mock_analyze_emotion(chat_text, profile_context)

        return validate_analysis_output(result, chat_text, profile_context)

    def _should_use_mock(self) -> bool:
        return settings.llm_mock_mode or settings.llm_provider.lower() in {"", "mock", "none"}

    def _mock_analyze_emotion(self, chat_text: str, profile_context: str = "") -> AnalyzeResponse:
        """Sinh kết quả mock để test ổn định khi chưa bật LLM thật."""
        normalized_text = self._normalize_for_matching(chat_text)
        context_lower = profile_context.lower()
        input_quality = self._estimate_input_quality(chat_text, context_lower)
        ocr_uncertainty = self._ocr_uncertainty_reasons(context_lower)

        affectionate_keywords = [
            "iu",
            "yeu",
            "yeuemm",
            "thuong",
            "nho",
            "om",
            "be",
            "ngu ngon",
            "hun",
        ]
        teasing_keywords = ["nho", "ca dut", "mong du", "duoc hong", "hihi", "haha", "hehe", "troll"]
        fatigue_keywords = ["met", "khong sao", "hoi la", "im lang", "nghi", "duoi", "mai noi", "noi sau"]
        sadness_keywords = ["buon", "tui", "khoc", "co don", "that vong"]
        anxiety_keywords = [
            "lo qua",
            "so",
            "bat an",
            "khong yen tam",
            "sao lau tra loi",
            "co sao khong",
            "em co on khong",
            "hoi hop",
        ]
        care_keywords = [
            "an chua",
            "uong nuoc",
            "di duong can than",
            "ve den nha",
            "bao anh",
            "bao em",
            "giu suc khoe",
            "nghi som",
            "em on khong",
            "anh o day",
        ]
        sulking_keywords = [
            "gian",
            "buc",
            "kho chiu",
            "dung hoi",
            "khong muon noi",
            "sao cung duoc",
            "muon lam gi thi lam",
            "thoi khoi",
            "mac ke",
        ]

        affection_score = self._keyword_score(normalized_text, affectionate_keywords)
        teasing_score = self._keyword_score(normalized_text, teasing_keywords)
        fatigue_score = self._keyword_score(normalized_text, fatigue_keywords)
        sadness_score = self._keyword_score(normalized_text, sadness_keywords)
        anxiety_score = self._keyword_score(normalized_text, anxiety_keywords)
        care_score = self._keyword_score(normalized_text, care_keywords)
        sulking_score = self._keyword_score(normalized_text, sulking_keywords)

        if self._is_insufficient_input(normalized_text):
            return self._insufficient_response(profile_context, context_lower, input_quality, ocr_uncertainty)

        if affection_score >= 2 or (affection_score >= 1 and teasing_score >= 1):
            return self._affectionate_teasing_response(
                chat_text,
                profile_context,
                context_lower,
                input_quality,
                ocr_uncertainty,
                affectionate_keywords + teasing_keywords,
            )

        if fatigue_score or "khong sao" in normalized_text:
            return self._fatigue_response(
                chat_text,
                profile_context,
                context_lower,
                input_quality,
                ocr_uncertainty,
                fatigue_keywords,
            )

        if sulking_score:
            return AnalyzeResponse(
                overall_emotion="khó chịu nhẹ / giận dỗi",
                confidence=0.68,
                emotion_distribution={
                    "than_mat": 0.0,
                    "treu_dua": 0.0,
                    "quan_tam": 0.0,
                    "met_moi": 0.0,
                    "ne_tranh": 0.18,
                    "kho_chiu": 0.62,
                    "trung_lap": 0.20,
                    "chua_du_du_lieu": 0.0,
                },
                summary=(
                    "Một số câu có sắc thái cụt, buông xuôi hoặc phản ứng phòng thủ nhẹ. "
                    "Điều này có thể liên quan đến khó chịu hoặc giận dỗi, nhưng vẫn cần hỏi lại trực tiếp để tránh suy diễn."
                ),
                context_note=self._build_context_note(profile_context, context_lower),
                suggested_reply=(
                    "Anh thấy có thể em đang không thoải mái. Anh không muốn hỏi dồn, khi nào em sẵn sàng thì mình nói chuyện nhẹ nhàng hơn nha."
                ),
                warning=WARNING_MESSAGE,
                tone="khó chịu nhẹ / giận dỗi",
                evidence=self._extract_evidence(
                    chat_text,
                    sulking_keywords,
                    label="khó chịu nhẹ / giận dỗi",
                    reason="Câu có sắc thái buông xuôi hoặc phòng thủ nhẹ, nên phản hồi bình tĩnh và tránh hỏi dồn.",
                ),
                uncertainty_reasons=[
                    *ocr_uncertainty,
                    "Các câu ngắn hoặc buông xuôi có thể bị hiểu nhầm nếu thiếu ngữ cảnh trước đó.",
                ],
                input_quality=input_quality,
                reply_style="bình tĩnh, không tranh cãi, không hỏi dồn",
            )

        if anxiety_score:
            return self._anxiety_response(
                chat_text,
                profile_context,
                context_lower,
                input_quality,
                ocr_uncertainty,
                anxiety_keywords,
            )

        if care_score:
            return self._care_response(
                chat_text,
                profile_context,
                context_lower,
                input_quality,
                ocr_uncertainty,
                care_keywords,
            )

        if sadness_score:
            return AnalyzeResponse(
                overall_emotion="buồn / cần được lắng nghe",
                confidence=0.7,
                emotion_distribution={
                    "than_mat": 0.0,
                    "treu_dua": 0.0,
                    "quan_tam": 0.12,
                    "met_moi": 0.22,
                    "ne_tranh": 0.0,
                    "kho_chiu": 0.0,
                    "trung_lap": 0.30,
                    "chua_du_du_lieu": 0.0,
                    "buon": 0.36,
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
                tone="buồn / cần được lắng nghe",
                evidence=self._extract_evidence(
                    chat_text,
                    sadness_keywords,
                    label="buồn / cần được lắng nghe",
                    reason="Câu chứa tín hiệu buồn hoặc hụt hẫng, phù hợp với phản hồi lắng nghe.",
                ),
                uncertainty_reasons=[
                    *ocr_uncertainty,
                    "Chỉ dựa trên vài câu chữ nên chưa thể biết chắc nguyên nhân cảm xúc.",
                ],
                input_quality=input_quality,
                reply_style="lắng nghe, xác nhận cảm xúc, tránh thúc ép",
            )

        if affection_score:
            return AnalyzeResponse(
                overall_emotion="ấm áp / tích cực",
                confidence=0.74,
                emotion_distribution={
                    "than_mat": 0.38,
                    "treu_dua": 0.16,
                    "quan_tam": 0.24,
                    "met_moi": 0.0,
                    "ne_tranh": 0.0,
                    "kho_chiu": 0.0,
                    "trung_lap": 0.22,
                    "chua_du_du_lieu": 0.0,
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
                tone="ấm áp / tích cực",
                evidence=self._extract_evidence(
                    chat_text,
                    affectionate_keywords,
                    label="thân mật / quan tâm",
                    reason="Câu có từ thân mật hoặc quan tâm rõ, không nên gộp vào trung lập thuần.",
                ),
                uncertainty_reasons=[
                    *ocr_uncertainty,
                    "Một vài từ thân mật có thể mang sắc thái đùa tùy thói quen nhắn tin của hai người.",
                ],
                input_quality=input_quality,
                reply_style="ấm áp, tự nhiên, đáp lại sự quan tâm",
            )

        return AnalyzeResponse(
            overall_emotion="trung lập / chưa đủ dữ liệu",
            confidence=0.56,
            emotion_distribution={
                "than_mat": 0.0,
                "treu_dua": 0.0,
                "quan_tam": 0.20,
                "met_moi": 0.18,
                "ne_tranh": 0.0,
                "kho_chiu": 0.0,
                "trung_lap": 0.42,
                "chua_du_du_lieu": 0.20,
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
            tone="chưa đủ dữ liệu rõ ràng",
            evidence=self._extract_evidence(
                chat_text,
                ["ok", "uh", "ừ", "vang", "ừm"],
                label="thiếu dữ liệu",
                reason="Câu quá ngắn nên không đủ căn cứ để phân loại sắc thái mạnh.",
                limit=2,
            ),
            uncertainty_reasons=[
                *ocr_uncertainty,
                "Đoạn chat chưa có đủ dấu hiệu rõ để phân loại sắc thái mạnh.",
            ],
            input_quality=input_quality,
            reply_style="hỏi thăm nhẹ, không suy diễn",
        )

    def _affectionate_teasing_response(
        self,
        chat_text: str,
        profile_context: str,
        context_lower: str,
        input_quality: str,
        uncertainty_reasons: list[str],
        evidence_keywords: list[str],
    ) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="thân mật / trêu đùa / quan tâm",
            confidence=0.76 if input_quality != "low" else 0.62,
            emotion_distribution={
                "than_mat": 0.34,
                "treu_dua": 0.28,
                "quan_tam": 0.24,
                "met_moi": 0.0,
                "ne_tranh": 0.0,
                "kho_chiu": 0.0,
                "trung_lap": 0.14,
                "chua_du_du_lieu": 0.0,
            },
            summary=(
                "Đoạn chat có nhiều tín hiệu gần gũi và trêu đùa nhẹ, nhất là các cách gọi thân mật, "
                "lời chúc ngủ ngon hoặc câu đùa về việc muốn được ôm. Không nên xem đây là kết luận chắc chắn, "
                "nhưng sắc thái tổng thể không phải trung lập thuần."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply=(
                "Nghe đáng yêu quá. Em nghỉ một chút nha, khi nào muốn nói chuyện tiếp thì anh vẫn ở đây nghe em."
            ),
            warning=WARNING_MESSAGE,
            tone="thân mật, trêu đùa nhẹ, có quan tâm",
            evidence=self._extract_evidence(
                chat_text,
                evidence_keywords,
                label="thân mật / trêu đùa / quan tâm",
                reason="Câu có từ thân mật, lời chúc hoặc cách đùa nhẹ cho thấy sắc thái gần gũi.",
            ),
            uncertainty_reasons=[
                *uncertainty_reasons,
                "Teencode, emoji hoặc câu đùa riêng của hai người có thể cần bạn chỉnh lại nếu OCR nhận sai.",
            ],
            input_quality=input_quality,
            reply_style="ấm áp, vui nhẹ, không phân tích quá nặng",
        )

    def _anxiety_response(
        self,
        chat_text: str,
        profile_context: str,
        context_lower: str,
        input_quality: str,
        uncertainty_reasons: list[str],
        evidence_keywords: list[str],
    ) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="lo lắng / cần trấn an nhẹ",
            confidence=0.66 if input_quality != "low" else 0.52,
            emotion_distribution={
                "than_mat": 0.0,
                "treu_dua": 0.0,
                "quan_tam": 0.18,
                "met_moi": 0.0,
                "ne_tranh": 0.0,
                "kho_chiu": 0.0,
                "trung_lap": 0.18,
                "chua_du_du_lieu": 0.0,
                "lo_lang": 0.64,
            },
            summary=(
                "Đoạn chat có dấu hiệu lo lắng hoặc cần được trấn an nhẹ. "
                "Không đủ dữ liệu để kết luận nguyên nhân, nhưng nên phản hồi rõ ràng và bình tĩnh."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply=(
                "Anh đây rồi, xin lỗi vì để em lo. Anh vẫn ổn, cảm ơn em đã quan tâm nha."
            ),
            warning=WARNING_MESSAGE,
            tone="lo lắng / cần trấn an nhẹ",
            evidence=self._extract_evidence(
                chat_text,
                evidence_keywords,
                label="lo lắng",
                reason="Câu thể hiện sự bất an, chờ phản hồi hoặc muốn biết người kia có ổn không.",
            ),
            uncertainty_reasons=[
                *uncertainty_reasons,
                "Lo lắng có thể đến từ bối cảnh ngoài đoạn chat, nên không kết luận nguyên nhân.",
            ],
            input_quality=input_quality,
            reply_style="trấn an rõ ràng, trả lời ngắn gọn, không trách ngược",
        )

    def _care_response(
        self,
        chat_text: str,
        profile_context: str,
        context_lower: str,
        input_quality: str,
        uncertainty_reasons: list[str],
        evidence_keywords: list[str],
    ) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="quan tâm / dịu dàng",
            confidence=0.7 if input_quality != "low" else 0.55,
            emotion_distribution={
                "than_mat": 0.12,
                "treu_dua": 0.0,
                "quan_tam": 0.58,
                "met_moi": 0.0,
                "ne_tranh": 0.0,
                "kho_chiu": 0.0,
                "trung_lap": 0.30,
                "chua_du_du_lieu": 0.0,
            },
            summary=(
                "Đoạn chat nghiêng về sự quan tâm và nhắc nhở nhẹ nhàng. "
                "Đây là tín hiệu giao tiếp tích cực, nhưng vẫn chỉ nên đọc như tham khảo."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply="Cảm ơn em nha, anh sẽ chú ý hơn. Em cũng nghỉ ngơi và giữ sức khỏe nhé.",
            warning=WARNING_MESSAGE,
            tone="quan tâm, dịu dàng",
            evidence=self._extract_evidence(
                chat_text,
                evidence_keywords,
                label="quan tâm",
                reason="Câu có nội dung hỏi thăm, nhắc nghỉ ngơi hoặc dặn an toàn.",
            ),
            uncertainty_reasons=[
                *uncertainty_reasons,
                "Một số câu hỏi thăm có thể là thói quen giao tiếp, không nên suy diễn sâu hơn.",
            ],
            input_quality=input_quality,
            reply_style="đón nhận, cảm ơn, đáp lại nhẹ nhàng",
        )

    def _fatigue_response(
        self,
        chat_text: str,
        profile_context: str,
        context_lower: str,
        input_quality: str,
        uncertainty_reasons: list[str],
        evidence_keywords: list[str],
    ) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="mệt mỏi / né tránh nhẹ",
            confidence=0.72,
            emotion_distribution={
                "than_mat": 0.0,
                "treu_dua": 0.0,
                "quan_tam": 0.0,
                "met_moi": 0.35,
                "ne_tranh": 0.25,
                "kho_chiu": 0.0,
                "trung_lap": 0.20,
                "chua_du_du_lieu": 0.0,
                "buon": 0.20,
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
            tone="mệt mỏi / cần khoảng lặng",
            evidence=self._extract_evidence(
                chat_text,
                evidence_keywords,
                label="mệt mỏi / né tránh nhẹ",
                reason="Câu cho thấy người nói mệt hoặc muốn lùi lại khỏi cuộc trò chuyện lúc đó.",
            ),
            uncertainty_reasons=[
                *uncertainty_reasons,
                "Các câu như 'không sao' hoặc 'mai nói' có thể là mệt thật, cũng có thể là chưa muốn nói lúc đó.",
            ],
            input_quality=input_quality,
            reply_style="nhẹ nhàng, cho không gian, không hỏi dồn",
        )

    def _insufficient_response(
        self,
        profile_context: str,
        context_lower: str,
        input_quality: str,
        uncertainty_reasons: list[str],
    ) -> AnalyzeResponse:
        return AnalyzeResponse(
            overall_emotion="chưa đủ dữ liệu",
            confidence=0.28,
            emotion_distribution={
                "than_mat": 0.0,
                "treu_dua": 0.0,
                "quan_tam": 0.0,
                "met_moi": 0.0,
                "ne_tranh": 0.0,
                "kho_chiu": 0.0,
                "trung_lap": 0.32,
                "chua_du_du_lieu": 0.68,
            },
            summary=(
                "Đoạn chat quá ngắn nên chưa đủ căn cứ để nhận diện sắc thái cảm xúc rõ ràng. "
                "Nên bổ sung thêm vài câu trước và sau nếu bạn muốn kết quả có ích hơn."
            ),
            context_note=self._build_context_note(profile_context, context_lower),
            suggested_reply="Mình chưa chắc đã hiểu đúng ý em. Nếu em muốn, mình nói thêm một chút nha.",
            warning=WARNING_MESSAGE,
            tone="chưa đủ dữ liệu",
            evidence=[],
            uncertainty_reasons=[
                *uncertainty_reasons,
                "Input quá ngắn nên confidence được hạ thấp để tránh suy diễn.",
            ],
            input_quality="low" if input_quality != "good" else "medium",
            reply_style="hỏi mở, không kết luận",
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

    def _normalize_for_matching(self, text: str) -> str:
        lowered = text.lower().replace("đ", "d")
        without_accents = "".join(
            char for char in unicodedata.normalize("NFD", lowered) if unicodedata.category(char) != "Mn"
        )
        return " ".join(without_accents.split())

    def _extract_evidence(
        self,
        chat_text: str,
        keywords: list[str],
        *,
        label: str,
        reason: str,
        limit: int = 4,
    ) -> list[EvidenceItem]:
        evidence: list[EvidenceItem] = []
        normalized_keywords = [self._normalize_for_matching(keyword) for keyword in keywords]

        for line in chat_text.splitlines():
            cleaned_line = line.strip()
            if not cleaned_line:
                continue

            normalized_line = self._normalize_for_matching(cleaned_line)
            if any(keyword and keyword in normalized_line for keyword in normalized_keywords):
                evidence.append(EvidenceItem(quote=cleaned_line, label=label, reason=reason))

            if len(evidence) >= limit:
                break

        return evidence

    def _is_insufficient_input(self, normalized_text: str) -> bool:
        compact = normalized_text.replace(" ", "")
        short_replies = {"ok", "oke", "uh", "um", "u", "vang", "da", "duoc", "khong"}
        return compact in short_replies or len(compact) < 5

    def _estimate_input_quality(self, chat_text: str, context_lower: str) -> str:
        compact_length = len("".join(chat_text.split()))
        line_count = len([line for line in chat_text.splitlines() if line.strip()])

        if compact_length < 20:
            return "low"
        if "ocr" in context_lower:
            return "medium" if compact_length >= 40 and line_count >= 2 else "low"
        return "good" if compact_length >= 40 and line_count >= 2 else "medium"

    def _ocr_uncertainty_reasons(self, context_lower: str) -> list[str]:
        if "ocr" not in context_lower:
            return []
        return ["Nội dung có thể chứa lỗi OCR, nên kiểm tra lại câu chữ trước khi đọc kết quả."]
