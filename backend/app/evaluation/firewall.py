"""
Fail-Closed Runtime GroundTruth Firewall (APT-052).
Runs immediately before model inference to detect forbidden gold annotations or sentinels.
"""

import json
import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel

from app.evaluation.schemas import GROUND_TRUTH_SENTINEL_71F2

logger = logging.getLogger("GroundTruthFirewall")

FORBIDDEN_FIREWALL_FIELDS: Set[str] = {
    "bug_status",
    "error_category",
    "bug_type",
    "bug_location",
    "knowledge_components",
    "possible_misconception",
    "reference_diagnosis",
    "reference_solution",
    "expected_behavior",
    "hint_1",
    "hint_2",
    "hint_3",
    "review_status",
}


class GroundTruthLeakageError(TypeError):
    """
    Exception raised when GroundTruthFirewall detects forbidden ground-truth fields
    or sentinel tokens in inference inputs.

    Inherits from TypeError to satisfy architectural type-level boundary enforcement
    while providing dedicated, fail-closed runtime provenance logging.
    Never sanitize silently - execution must abort immediately.
    """

    def __init__(
        self,
        sample_id: str,
        field_path: str,
        message: str,
        run_id: Optional[str] = None,
    ):
        self.sample_id = sample_id
        self.field_path = field_path
        self.run_id = run_id
        super().__init__(
            f"[GroundTruthFirewall VIOLATION] Execution halted: sample_id='{sample_id}', "
            f"run_id='{run_id or 'none'}', detected_path='{field_path}'. Reason: {message}"
        )


class GroundTruthFirewall:
    """
    Fail-closed runtime firewall that inspects prompts, messages, payloads,
    and student context immediately before any research model invocation.
    """

    def __init__(
        self,
        forbidden_fields: Optional[Set[str]] = None,
        sentinel: str = GROUND_TRUTH_SENTINEL_71F2,
    ):
        self.forbidden_fields = set(f.lower() for f in (forbidden_fields or FORBIDDEN_FIREWALL_FIELDS))
        self.sentinel = sentinel

    @classmethod
    def default(cls) -> "GroundTruthFirewall":
        return cls()

    def inspect(
        self,
        target: Any,
        sample_id: str = "unknown",
        run_id: Optional[str] = None,
        base_path: str = "root",
    ) -> None:
        """
        Deep recursively scan arbitrary Python objects, dicts, lists, Pydantic models,
        strings, and JSON serializations for forbidden keys or sentinel tokens.
        """
        self._scan_node(target, sample_id=sample_id, run_id=run_id, current_path=base_path)

    def _scan_node(
        self,
        node: Any,
        sample_id: str,
        run_id: Optional[str],
        current_path: str,
    ) -> None:
        if node is None:
            return

        # 1. Pydantic Model
        if isinstance(node, BaseModel):
            cls_name = node.__class__.__name__
            if cls_name == "GroundTruth":
                self._report_violation(
                    sample_id=sample_id,
                    run_id=run_id,
                    field_path=current_path,
                    message="GroundTruth object passed to inference component!",
                )
            if cls_name == "EvaluationMetadata":
                self._report_violation(
                    sample_id=sample_id,
                    run_id=run_id,
                    field_path=current_path,
                    message="EvaluationMetadata object passed to inference component!",
                )
            if cls_name == "EvaluationRecord":
                self._report_violation(
                    sample_id=sample_id,
                    run_id=run_id,
                    field_path=current_path,
                    message="Combined EvaluationRecord passed to inference component!",
                )
            model_dict = node.model_dump()
            self._scan_node(model_dict, sample_id, run_id, current_path)
            return

        # 2. Dataclass
        if is_dataclass(node) and not isinstance(node, type):
            dc_dict = asdict(node)
            self._scan_node(dc_dict, sample_id, run_id, current_path)
            return

        # 3. Dictionary
        if isinstance(node, dict):
            for key, val in node.items():
                str_key = str(key).strip().lower()
                child_path = f"{current_path}.{key}"

                # Check if key name is forbidden
                if str_key in self.forbidden_fields:
                    self._report_violation(
                        sample_id=sample_id,
                        run_id=run_id,
                        field_path=child_path,
                        message=f"Forbidden ground-truth field name '{key}' detected in dictionary keys.",
                    )

                # Check if key string itself contains sentinel
                if self.sentinel in str(key):
                    self._report_violation(
                        sample_id=sample_id,
                        run_id=run_id,
                        field_path=child_path,
                        message="GroundTruth sentinel detected in dictionary key string.",
                    )

                # Recursively inspect value
                self._scan_node(val, sample_id, run_id, child_path)
            return

        # 4. List, Tuple, Set
        if isinstance(node, (list, tuple, set)):
            for idx, item in enumerate(node):
                child_path = f"{current_path}[{idx}]"
                self._scan_node(item, sample_id, run_id, child_path)
            return

        # 5. String
        if isinstance(node, str):
            # Check for sentinel token in string
            if self.sentinel in node:
                self._report_violation(
                    sample_id=sample_id,
                    run_id=run_id,
                    field_path=current_path,
                    message="GroundTruth sentinel detected in string value.",
                )

            # Check if string is a serialized JSON object containing forbidden keys
            stripped = node.strip()
            if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
                try:
                    parsed_json = json.loads(stripped)
                    self._scan_node(parsed_json, sample_id, run_id, f"{current_path}<json>")
                except (json.JSONDecodeError, ValueError):
                    pass
            return

    def _report_violation(
        self,
        sample_id: str,
        run_id: Optional[str],
        field_path: str,
        message: str,
    ) -> None:
        """
        Log safe privacy-preserving violation notice and raise GroundTruthLeakageError.
        CRITICAL: Never log private code or gold content.
        """
        logger.error(
            "GROUND_TRUTH_FIREWALL_VIOLATION | sample_id=%s | run_id=%s | path=%s",
            sample_id,
            run_id or "none",
            field_path,
        )
        raise GroundTruthLeakageError(
            sample_id=sample_id,
            field_path=field_path,
            message=message,
            run_id=run_id,
        )

    def inspect_request(
        self,
        *,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        messages: Optional[List[Any]] = None,
        student_context: Optional[Any] = None,
        payload: Optional[Any] = None,
        sample_id: str = "unknown",
        run_id: Optional[str] = None,
    ) -> None:
        """
        Convenience inspector checking all standard request components simultaneously.
        """
        if system_prompt is not None:
            self.inspect(system_prompt, sample_id=sample_id, run_id=run_id, base_path="system_prompt")
        if user_prompt is not None:
            self.inspect(user_prompt, sample_id=sample_id, run_id=run_id, base_path="user_prompt")
        if messages is not None:
            self.inspect(messages, sample_id=sample_id, run_id=run_id, base_path="messages")
        if student_context is not None:
            self.inspect(student_context, sample_id=sample_id, run_id=run_id, base_path="student_context")
        if payload is not None:
            self.inspect(payload, sample_id=sample_id, run_id=run_id, base_path="payload")
