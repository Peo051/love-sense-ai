"""
Unit Tests for Fail-Closed GroundTruth Firewall (APT-052).

Verifies:
1. Direct forbidden gold keys trigger GroundTruthLeakageError immediately.
2. Deeply nested forbidden keys trigger GroundTruthLeakageError with accurate path reporting.
3. Renamed containers harboring the sentinel trigger GroundTruthLeakageError.
4. Student context contamination triggers GroundTruthLeakageError.
5. Serialized string / JSON payloads containing forbidden keys or sentinels are intercepted.
6. Clean ModelInput passes through the firewall smoothly.
7. Logs do NOT leak sensitive student code or gold values (privacy compliance).
8. Provider client execution is aborted before invocation.
"""

from typing import Any, Dict
import pytest

from app.evaluation.firewall import (
    FORBIDDEN_FIREWALL_FIELDS,
    GroundTruthFirewall,
    GroundTruthLeakageError,
)
from app.evaluation.schemas import (
    GROUND_TRUTH_SENTINEL_71F2,
    GroundTruth,
    ModelInput,
)
from app.tutor.provider import DeterministicMockTutorProvider


@pytest.fixture
def firewall() -> GroundTruthFirewall:
    return GroundTruthFirewall.default()


def test_direct_forbidden_key(firewall: GroundTruthFirewall):
    """
    Requirement: Direct forbidden key in dict triggers GroundTruthLeakageError.
    """
    for forbidden_key in FORBIDDEN_FIREWALL_FIELDS:
        payload = {forbidden_key: "some_gold_value", "clean_field": "ok"}
        with pytest.raises(GroundTruthLeakageError) as exc_info:
            firewall.inspect(payload, sample_id="test-direct-01", run_id="run-01")

        err = exc_info.value
        assert err.sample_id == "test-direct-01"
        assert err.run_id == "run-01"
        assert forbidden_key in err.field_path
        assert "Forbidden ground-truth field name" in str(err)


def test_nested_forbidden_key(firewall: GroundTruthFirewall):
    """
    Requirement: Nested forbidden key at arbitrary depth triggers GroundTruthLeakageError with path.
    """
    payload = {
        "metadata": {
            "diagnostics": {
                "layers": [
                    {"layer_id": 1, "status": "ok"},
                    {"layer_id": 2, "bug_type": "encapsulation_break"},
                ]
            }
        }
    }

    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect(payload, sample_id="test-nested-02")

    err = exc_info.value
    assert err.sample_id == "test-nested-02"
    assert "metadata.diagnostics.layers[1].bug_type" in err.field_path


def test_renamed_container_containing_sentinel(firewall: GroundTruthFirewall):
    """
    Requirement: Renamed container containing sentinel value triggers GroundTruthLeakageError.
    """
    payload = {
        "harmless_wrapper": {
            "innocent_field": f"Some hidden telemetry with {GROUND_TRUTH_SENTINEL_71F2} inside"
        }
    }

    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect(payload, sample_id="test-sentinel-03")

    err = exc_info.value
    assert err.sample_id == "test-sentinel-03"
    assert "harmless_wrapper.innocent_field" in err.field_path
    assert "sentinel detected" in str(err)


def test_student_context_contamination(firewall: GroundTruthFirewall):
    """
    Requirement: Contaminated student context triggers GroundTruthLeakageError.
    """
    # 1. Contaminated with knowledge_components
    bad_context_kc = {
        "attempt_count": 2,
        "knowledge_components": ["csharp.encapsulation"],
    }
    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect_request(
            student_context=bad_context_kc,
            sample_id="test-ctx-04",
        )
    assert "student_context.knowledge_components" in exc_info.value.field_path

    # 2. Contaminated with possible_misconception
    bad_context_misc = {
        "attempt_count": 1,
        "possible_misconception": "Believes public is safe",
    }
    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect_request(
            student_context=bad_context_misc,
            sample_id="test-ctx-05",
        )
    assert "student_context.possible_misconception" in exc_info.value.field_path


def test_serialized_object_contamination(firewall: GroundTruthFirewall):
    """
    Requirement: Serialized JSON payload containing forbidden keys triggers GroundTruthLeakageError.
    """
    serialized_payload = '{"request": {"student_code": "code", "reference_solution": "solution"}}'

    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect(serialized_payload, sample_id="test-serialized-06")

    err = exc_info.value
    assert err.sample_id == "test-serialized-06"
    assert "reference_solution" in err.field_path


def test_clean_model_input_passes(firewall: GroundTruthFirewall):
    """
    Requirement: Clean ModelInput passes through the firewall without any exception.
    """
    model_input = ModelInput(
        sample_id="vct-clean-01",
        problem_statement="Xây dựng lớp Rectangle tính diện tích.",
        student_code="public class Rectangle { public int W; public int H; }",
        compiler_error="CS0161: Not all code paths return a value",
        student_question="Làm sao để return diện tích?",
    )

    # Inspect as object
    firewall.inspect(model_input, sample_id=model_input.sample_id)

    # Inspect as dict
    firewall.inspect(model_input.to_model_dict(), sample_id=model_input.sample_id)

    # Inspect as request
    firewall.inspect_request(
        user_prompt="Explain error",
        student_context={"attempt_count": 1, "struggling_kcs": []},
        payload=model_input,
        sample_id=model_input.sample_id,
    )


def test_privacy_in_error_message(firewall: GroundTruthFirewall):
    """
    Requirement: Firewall error message must NOT log raw code or gold contents.
    Must only record sample_id, run_id, and detected path.
    """
    private_secret_code = "SECRET_INTELLECTUAL_PROPERTY_12345"
    payload = {
        "bug_location": private_secret_code,
    }

    with pytest.raises(GroundTruthLeakageError) as exc_info:
        firewall.inspect(payload, sample_id="vct-priv-01", run_id="run-safe-99")

    err_str = str(exc_info.value)
    assert "vct-priv-01" in err_str
    assert "run-safe-99" in err_str
    assert "bug_location" in err_str
    assert private_secret_code not in err_str, "Private content leaked into exception message!"


@pytest.mark.anyio
async def test_no_provider_call_after_firewall_failure():
    """
    Requirement: Ensure provider call is aborted and not recorded if firewall trips.
    """
    provider = DeterministicMockTutorProvider()
    contaminated_messages = [
        {"role": "user", "content": "Hello", "bug_status": "has_bug"}
    ]

    with pytest.raises(GroundTruthLeakageError):
        await provider.generate_response(contaminated_messages)

    # Recorded messages must remain empty because firewall tripped before execution
    assert len(provider.recorded_messages) == 0
