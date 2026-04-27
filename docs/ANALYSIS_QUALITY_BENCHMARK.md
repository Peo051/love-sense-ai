# Emotion Analysis Quality Benchmark

This benchmark is a regression test suite for Love Sense AI's conversation tone analysis pipeline.

It is not a ground truth dataset and must not be treated as a definitive psychological or emotional label source. The cases are synthetic examples written for engineering validation only. They help catch regressions such as:

- affectionate or teasing chat being collapsed into plain neutral,
- short input receiving high confidence,
- tired or avoidant phrasing being misread as irritation,
- irritation being misread as care or intimacy,
- care/check-in messages being missed by the mock fallback,
- anxiety/worry signals being ignored.

## Dataset

The benchmark cases live in:

```text
data/evaluation/chat_sentiment_cases.json
```

Each case includes:

- `chat_text`: synthetic chat content used only for tests.
- `expected_labels`: labels that should be present in the result.
- `disallowed_labels`: labels that would be a serious regression if returned as a major signal.
- `expected_confidence_range`: acceptable confidence bounds for the mock fallback.
- `notes`: short context for maintainers.

No real user chat, screenshots, private names, API keys, tokens, or secrets should be added to this dataset.

## Test Scope

The backend test `backend/tests/test_analysis_benchmark.py` runs the current mock analysis pipeline against the benchmark. It checks that the output:

- stays within the expected confidence range,
- includes the expected label signals,
- does not return disallowed labels as major signals,
- provides evidence for non-low-confidence cases.

The benchmark intentionally validates regression behavior, not model truth. Human communication is contextual, and Love Sense AI must continue to present results as suggestions only.

## Updating Cases

When adding cases:

1. Use synthetic content only.
2. Keep labels broad and safety-oriented.
3. Avoid labels that imply certainty about another person's inner state.
4. Prefer testing serious misclassification risks over minor wording preferences.
5. Keep confidence ranges moderate, especially for short or OCR-like text.
