import asyncio
import json
import re
import unicodedata
from pathlib import Path

import pytest

from app.services.ai_service import AIService


BENCHMARK_PATH = Path(__file__).resolve().parents[2] / "data" / "evaluation" / "chat_sentiment_cases.json"
MIN_SIGNAL_SCORE = 0.12
MAJOR_WRONG_SCORE = 0.25


def load_cases() -> list[dict]:
    with BENCHMARK_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def normalize_label(value: str) -> str:
    lowered = value.lower().replace("đ", "d")
    without_accents = "".join(
        char for char in unicodedata.normalize("NFD", lowered) if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", "_", without_accents).strip("_")


def text_matches_label(text: str, label: str) -> bool:
    normalized_text = normalize_label(text)
    normalized_label = normalize_label(label)
    return normalized_label in normalized_text


def analysis_has_expected_label(result, expected_label: str) -> bool:
    normalized_expected = normalize_label(expected_label)

    for label, score in result.emotion_distribution.items():
        if normalize_label(label) == normalized_expected and score >= MIN_SIGNAL_SCORE:
            return True

    text_parts = [
        result.overall_emotion,
        result.tone or "",
        *(item.label for item in result.evidence),
    ]
    return any(text_matches_label(part, normalized_expected) for part in text_parts)


def analysis_has_major_disallowed_label(result, disallowed_label: str) -> bool:
    normalized_disallowed = normalize_label(disallowed_label)

    for label, score in result.emotion_distribution.items():
        if normalize_label(label) == normalized_disallowed and score >= MAJOR_WRONG_SCORE:
            return True

    text_parts = [result.overall_emotion, result.tone or "", *(item.label for item in result.evidence)]
    return any(text_matches_label(part, normalized_disallowed) for part in text_parts)


def analyze(chat_text: str):
    return asyncio.run(AIService().analyze_emotion(chat_text, "Benchmark synthetic case."))


def test_benchmark_dataset_shape():
    cases = load_cases()

    assert len(cases) >= 20
    for case in cases:
        assert case["chat_text"].strip()
        assert case["expected_labels"]
        assert isinstance(case["disallowed_labels"], list)
        assert len(case["expected_confidence_range"]) == 2
        assert case["notes"].strip()


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["id"])
def test_mock_analysis_benchmark_does_not_return_major_wrong_labels(case: dict):
    result = analyze(case["chat_text"])
    min_confidence, max_confidence = case["expected_confidence_range"]

    assert min_confidence <= result.confidence <= max_confidence

    missing_labels = [
        label for label in case["expected_labels"] if not analysis_has_expected_label(result, label)
    ]
    assert not missing_labels, f"Missing expected labels {missing_labels} for {case['id']}: {result.model_dump()}"

    wrong_labels = [
        label for label in case["disallowed_labels"] if analysis_has_major_disallowed_label(result, label)
    ]
    assert not wrong_labels, f"Returned disallowed labels {wrong_labels} for {case['id']}: {result.model_dump()}"

    if result.confidence >= 0.45:
        assert result.evidence, f"Expected evidence for non-low-confidence case {case['id']}"
