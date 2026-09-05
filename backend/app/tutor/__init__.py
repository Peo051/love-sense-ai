"""
Package điều phối gia sư lập trình thích ứng (Adaptive Programming Tutor).
"""

from app.schemas.tutor_schema import DiagnosisCategory
from app.tutor.diagnosis import DiagnosisSubsystem
from app.tutor.provider import (
    DeterministicMockTutorProvider,
    OpenAITutorProvider,
    TutorLLMProvider,
    TutorProviderError,
)
from app.tutor.service import TutorService, TutorServiceError
from app.tutor.taxonomy import (
    TAXONOMY_ISSUE_TYPES,
    normalize_category,
    normalize_diagnosis_labels,
    normalize_issue_type,
)
from app.tutor.validator import TutorOutputValidationError, TutorOutputValidator

__all__ = [
    "DiagnosisCategory",
    "DiagnosisSubsystem",
    "DeterministicMockTutorProvider",
    "OpenAITutorProvider",
    "TAXONOMY_ISSUE_TYPES",
    "TutorLLMProvider",
    "TutorOutputValidationError",
    "TutorOutputValidator",
    "TutorProviderError",
    "TutorService",
    "TutorServiceError",
    "normalize_category",
    "normalize_diagnosis_labels",
    "normalize_issue_type",
]
