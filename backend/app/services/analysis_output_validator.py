import re
import unicodedata
from difflib import SequenceMatcher

from app.schemas.analyze_schema import AnalyzeResponse, EvidenceItem
from app.services.analysis_policy import WARNING_MESSAGE

DEFAULT_DISTRIBUTION_KEYS = (
    "than_mat",
    "treu_dua",
    "quan_tam",
    "met_moi",
    "ne_tranh",
    "kho_chiu",
    "trung_lap",
    "chua_du_du_lieu",
)

UNSAFE_CLAIM_KEYWORDS = (
    "het yeu",
    "phan boi",
    "lua doi",
    "chac chan",
)

SAFE_SUMMARY = (
    "Đoạn chat chưa đủ để kết luận về cảm xúc thật của người khác. "
    "Hãy xem kết quả như tín hiệu tham khảo và ưu tiên giao tiếp trực tiếp."
)
SAFE_REPLY = "Mình muốn hiểu đúng hơn nên sẽ hỏi nhẹ nhàng, không suy diễn và không gây áp lực."
SAFE_CONTEXT_NOTE = "Bối cảnh chỉ được dùng để cá nhân hóa gợi ý phản hồi, không dùng để kết luận thay người khác."


def validate_analysis_output(
    result: AnalyzeResponse,
    chat_text: str,
    profile_context: str = "",
) -> AnalyzeResponse:
    """Validate and normalize analysis output before returning it to the client."""
    context_lower = profile_context.lower()
    evidence = _normalize_evidence(result.evidence, chat_text)
    uncertainty_reasons = _sanitize_text_list(result.uncertainty_reasons, limit=4)
    confidence = _normalize_confidence(
        result.confidence,
        chat_text=chat_text,
        context_lower=context_lower,
        has_evidence=bool(evidence),
        uncertainty_reasons=uncertainty_reasons,
    )

    return AnalyzeResponse(
        overall_emotion=_safe_text(result.overall_emotion, "chưa đủ dữ liệu"),
        confidence=confidence,
        emotion_distribution=_normalize_distribution(result.emotion_distribution),
        summary=_safe_text(result.summary, SAFE_SUMMARY),
        context_note=_safe_text(result.context_note, SAFE_CONTEXT_NOTE),
        suggested_reply=_safe_text(result.suggested_reply, SAFE_REPLY),
        warning=_normalize_warning(result.warning),
        tone=_safe_optional_text(result.tone),
        evidence=evidence,
        uncertainty_reasons=uncertainty_reasons,
        input_quality=_normalize_input_quality(result.input_quality, chat_text, context_lower),
        reply_style=_safe_optional_text(result.reply_style),
    )


def normalize_distribution_key(value: str) -> str:
    lowered = value.lower().replace("đ", "d")
    without_accents = "".join(
        char for char in unicodedata.normalize("NFD", lowered) if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", "_", without_accents).strip("_")


def _normalize_text_for_compare(value: str) -> str:
    return normalize_distribution_key(value).replace("_", " ")


def _normalize_warning(value: str) -> str:
    if isinstance(value, str) and "tham khảo" in value.lower():
        return value.strip()
    return WARNING_MESSAGE


def _safe_text(value: str, fallback: str) -> str:
    cleaned = value.strip() if isinstance(value, str) else ""
    if not cleaned or _contains_unsafe_claim(cleaned):
        return fallback
    return cleaned


def _safe_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned or _contains_unsafe_claim(cleaned):
        return None
    return cleaned


def _sanitize_text_list(values: list[str], *, limit: int) -> list[str]:
    cleaned_values: list[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        cleaned = _safe_text(value, "")
        if cleaned:
            cleaned_values.append(cleaned)
    return cleaned_values[:limit]


def _contains_unsafe_claim(value: str) -> bool:
    normalized = _normalize_text_for_compare(value)
    return any(keyword in normalized for keyword in UNSAFE_CLAIM_KEYWORDS)


def _normalize_distribution(distribution: dict[str, float]) -> dict[str, float]:
    normalized: dict[str, float] = {key: 0.0 for key in DEFAULT_DISTRIBUTION_KEYS}

    for label, raw_score in distribution.items():
        key = normalize_distribution_key(str(label))
        if not key:
            continue
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0
        normalized[key] = normalized.get(key, 0.0) + min(1.0, max(0.0, score))

    total = sum(normalized.values())
    if total <= 0:
        normalized["trung_lap"] = 0.55
        normalized["chua_du_du_lieu"] = 0.45
        return normalized

    return {label: score / total for label, score in normalized.items()}


def _normalize_evidence(values: list[EvidenceItem], chat_text: str) -> list[EvidenceItem]:
    normalized: list[EvidenceItem] = []

    for value in values:
        quote = value.quote.strip()
        label = _safe_text(value.label, "tín hiệu hội thoại")
        reason = _safe_text(value.reason, "Câu này được dùng làm căn cứ tham khảo cho phân tích.")
        if not quote or _contains_unsafe_claim(quote):
            continue
        if not _quote_is_supported_by_chat(quote, chat_text):
            continue
        normalized.append(EvidenceItem(quote=quote, label=label, reason=reason))
        if len(normalized) >= 4:
            break

    return normalized


def _quote_is_supported_by_chat(quote: str, chat_text: str) -> bool:
    normalized_quote = _normalize_text_for_compare(quote)
    normalized_chat = _normalize_text_for_compare(chat_text)

    if len(normalized_quote) < 4:
        return normalized_quote in normalized_chat

    if normalized_quote in normalized_chat:
        return True

    for line in chat_text.splitlines():
        normalized_line = _normalize_text_for_compare(line)
        if not normalized_line:
            continue
        if normalized_quote in normalized_line or normalized_line in normalized_quote:
            return True
        if SequenceMatcher(None, normalized_quote, normalized_line).ratio() >= 0.72:
            return True

    return False


def _normalize_confidence(
    confidence: float,
    *,
    chat_text: str,
    context_lower: str,
    has_evidence: bool,
    uncertainty_reasons: list[str],
) -> float:
    normalized = min(1.0, max(0.0, float(confidence)))

    if _is_short_chat(chat_text):
        normalized = min(normalized, 0.45)
        _append_once(uncertainty_reasons, "Đoạn chat quá ngắn nên confidence được giới hạn để tránh suy diễn.")

    if _has_low_ocr_quality(context_lower):
        normalized = min(normalized, 0.65)
        _append_once(uncertainty_reasons, "OCR có cảnh báo chất lượng nên confidence được giới hạn.")

    if not has_evidence:
        normalized = min(normalized, 0.6)
        _append_once(uncertainty_reasons, "Không có câu làm căn cứ rõ ràng nên confidence được giới hạn.")

    return normalized


def _normalize_input_quality(input_quality: str, chat_text: str, context_lower: str) -> str:
    value = input_quality.strip().lower() if isinstance(input_quality, str) else "medium"
    if value not in {"good", "medium", "low"}:
        value = "medium"

    if _is_short_chat(chat_text) or _has_low_ocr_quality(context_lower):
        return "low"
    return value


def _is_short_chat(chat_text: str) -> bool:
    compact = "".join(chat_text.split())
    return len(compact) < 20


def _has_low_ocr_quality(context_lower: str) -> bool:
    if "ocr" not in context_lower:
        return False
    low_quality_signals = (
        "cảnh báo ocr",
        "ocr nhận diện quá ít",
        "ocr chưa nhận diện",
        "ocr có thể chưa chính xác",
        "ảnh mờ",
        "chữ nhỏ",
        "nhiều ký tự khó đọc",
        "nền nhiều họa tiết",
    )
    return any(signal in context_lower for signal in low_quality_signals)


def _append_once(values: list[str], message: str) -> None:
    if message not in values:
        values.append(message)
