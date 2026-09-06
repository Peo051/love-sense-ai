"""
Package điều phối gia sư lập trình thích ứng (Adaptive Programming Tutor).
"""

from app.schemas.tutor_schema import DiagnosisCategory
from app.tutor.diagnosis import DiagnosisSubsystem
from app.tutor.evidence_grounding import EvidenceGroundingValidator, GroundingResult
from app.tutor.guest_context import (
    GuestContextError,
    GuestContextSigner,
    GuestContextTamperedError,
)
from app.tutor.hint_manager import HintManager, HintPayload, HintSessionState
from app.tutor.leakage_guard import LeakageCheckResult, SolutionLeakageGuard
from app.tutor.provider import (
    DeterministicMockTutorProvider,
    OpenAITutorProvider,
    TutorLLMProvider,
    TutorProviderError,
)
from app.tutor.service import TutorService, TutorServiceError
from app.tutor.skill_taxonomy import (
    CSHARP_OOP_SKILLS_V1,
    Skill,
    SkillTaxonomy,
)
from app.tutor.taxonomy import (
    TAXONOMY_ISSUE_TYPES,
    normalize_category,
    normalize_diagnosis_labels,
    normalize_issue_type,
)
from app.tutor.validator import TutorOutputValidationError, TutorOutputValidator
from app.tutor.verification import (
    ExecutionBackend,
    SandboxedCompilerBackend,
    StaticAndPatternExecutionBackend,
    VerificationService,
)

__all__ = [
    "CSHARP_OOP_SKILLS_V1",
    "DiagnosisCategory",
    "DiagnosisSubsystem",
    "DeterministicMockTutorProvider",
    "EvidenceGroundingValidator",
    "ExecutionBackend",
    "GroundingResult",
    "GuestContextError",
    "GuestContextSigner",
    "GuestContextTamperedError",
    "HintManager",
    "HintPayload",
    "HintSessionState",
    "LeakageCheckResult",
    "OpenAITutorProvider",
    "SandboxedCompilerBackend",
    "Skill",
    "SkillTaxonomy",
    "SolutionLeakageGuard",
    "StaticAndPatternExecutionBackend",
    "TAXONOMY_ISSUE_TYPES",
    "TutorLLMProvider",
    "TutorOutputValidationError",
    "TutorOutputValidator",
    "TutorProviderError",
    "TutorService",
    "TutorServiceError",
    "VerificationService",
    "normalize_category",
    "normalize_diagnosis_labels",
    "normalize_issue_type",
]

