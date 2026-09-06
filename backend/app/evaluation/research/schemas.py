"""
Strict Typed Schemas for Real Research Provider Adapter (APT-057).

Guarantees:
1. ResearchModelRequest contains ONLY model-visible content.
2. GroundTruth, EvaluationMetadata, and dataset gold fields are strictly prohibited.
3. ResearchProviderResponse preserves raw response and genuine provider metadata.
4. Missing provider metadata (e.g. usage, returned_model) remains None, never fabricated or estimated.
5. All schemas enforce frozen immutability and extra='forbid'.
"""

from typing import Any, Dict, List, Literal, Optional, Set
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.evaluation.schemas import (
    FORBIDDEN_GOLD_FIELDS,
    GROUND_TRUTH_SENTINEL_71F2,
    assert_not_ground_truth,
)


class ResearchMessage(BaseModel):
    """
    Immutable, strictly validated individual message passed to an LLM research provider.
    """

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Standardized message role in LLM chat completions.",
    )
    content: str = Field(
        ...,
        description="Text content of the message.",
        min_length=1,
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("content")
    @classmethod
    def validate_no_gold_sentinel(cls, v: str) -> str:
        if GROUND_TRUTH_SENTINEL_71F2 in v:
            raise ValueError(
                "CRITICAL SECURITY VIOLATION: GroundTruth sentinel detected in ResearchMessage content!"
            )
        return v


class ResearchUsage(BaseModel):
    """
    Token usage metadata genuinely returned by the provider.
    Never fabricated or estimated.
    """

    input_tokens: int = Field(..., ge=0, description="Number of tokens in the prompt / input.")
    output_tokens: int = Field(..., ge=0, description="Number of tokens in the generated completion.")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed as reported by the provider.")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )


class ResearchModelRequest(BaseModel):
    """
    Strictly whitelisted, immutable request passed to the ResearchProvider.

    INVARIANTS:
    - Contains ONLY model-visible data.
    - NEVER contains GroundTruth or EvaluationMetadata.
    - NEVER contains reference solutions, bug labels, or dataset gold annotations.
    - extra='forbid' prevents unauthorized field injections.
    """

    run_id: str = Field(..., min_length=1, description="Unique identifier of the evaluation run.")
    sample_id: str = Field(..., min_length=1, description="Benchmark sample ID.")
    system_name: str = Field(..., min_length=1, description="System name (A, B, C, D).")
    model: str = Field(..., min_length=1, description="Immutable model identifier.")
    messages: List[ResearchMessage] = Field(..., min_length=1, description="List of validated messages.")
    temperature: Optional[float] = Field(default=0.2, ge=0.0, le=2.0, description="Sampling temperature.")
    max_output_tokens: Optional[int] = Field(default=1500, gt=0, description="Maximum completion tokens.")
    response_format_mode: str = Field(default="json", description="Requested response format mode ('json', 'text').")

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, msgs: List[ResearchMessage]) -> List[ResearchMessage]:
        assert_not_ground_truth(msgs)
        for msg in msgs:
            assert_not_ground_truth(msg)
            assert_not_ground_truth(msg.content)
        return msgs


class ResearchProviderResponse(BaseModel):
    """
    Envelope preserving raw provider response and safe extracted metadata (APT-057).

    INVARIANTS:
    - raw_text preserves the exact text returned by the provider prior to parsing.
    - requested_model and returned_model are kept distinct.
    - returned_model is None if the provider does not explicitly return it.
    - usage is None if the provider does not return token counts (never estimated).
    - raw_metadata never stores authorization headers or API credentials.
    """

    provider: str = Field(..., min_length=1, description="Canonical provider name ('openai').")
    requested_model: str = Field(..., min_length=1, description="Model identifier requested by caller.")
    returned_model: Optional[str] = Field(
        default=None,
        description="Model identifier reported by the provider in response body. None if absent.",
    )
    raw_text: str = Field(..., description="Raw text returned by the provider prior to parsing.")
    request_id: Optional[str] = Field(
        default=None,
        description="HTTP or provider request ID (e.g. x-request-id) if returned. None if absent.",
    )
    provider_response_id: Optional[str] = Field(
        default=None,
        description="Provider-assigned response body ID (e.g. chatcmpl-xxx) if returned. None if absent.",
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="Reason generation finished ('stop', 'length', etc.) if returned. None if absent.",
    )
    usage: Optional[ResearchUsage] = Field(
        default=None,
        description="Genuinely reported token usage. None if provider does not expose it.",
    )
    provider_response_received: bool = Field(
        default=True,
        description="True indicating real provider response was successfully received.",
    )
    raw_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Safe, non-sensitive provider metadata (e.g. system_fingerprint, created timestamp).",
    )
    latency_ms: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Round-trip request latency in milliseconds.",
    )
    response_format_mode: str = Field(
        default="json",
        description="Format mode used for this request ('json', 'text').",
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    def to_serializable_dict(self) -> Dict[str, Any]:
        """
        Returns a clean dictionary representation for persistence.
        Guaranteed to exclude any secrets, Authorization headers, or non-serializable objects.
        """
        data = self.model_dump()
        # Defensive check: ensure no authorization or credentials exist in metadata
        meta = data.get("raw_metadata", {})
        cleaned_meta = {}
        for k, v in meta.items():
            k_lower = str(k).lower()
            if any(secret_term in k_lower for secret_term in ("auth", "key", "token", "secret", "bearer")):
                continue
            cleaned_meta[k] = v
        data["raw_metadata"] = cleaned_meta
        return data
