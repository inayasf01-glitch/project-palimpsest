"""Core data models for PALIMPSEST investigations."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Hypothesis:
    """A possible explanation for an investigated event."""

    id: str
    description: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Hypothesis ID cannot be empty.")
        if not self.description.strip():
            raise ValueError("Hypothesis description cannot be empty.")


@dataclass(frozen=True)
class Evidence:
    """A recorded observation with source provenance."""

    id: str
    statement: str
    source_id: str
    observed_at: datetime

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Evidence ID cannot be empty.")
        if not self.statement.strip():
            raise ValueError("Evidence statement cannot be empty.")
        if not self.source_id.strip():
            raise ValueError("Evidence source ID cannot be empty.")

        if (
            self.observed_at.tzinfo is None
            or self.observed_at.utcoffset() is None
        ):
            raise ValueError(
                "Evidence timestamp must include a timezone."
            )


@dataclass(frozen=True)
class InvestigationCase:
    """A case and its evaluation metadata.

    Ground truth is for evaluation only. It must not be passed to
    the investigator as evidence.
    """

    id: str
    title: str
    description: str
    hypotheses: tuple[Hypothesis, ...]
    evidence: tuple[Evidence, ...]
    ground_truth_hypothesis_id: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Case ID cannot be empty.")
        if not self.title.strip():
            raise ValueError("Case title cannot be empty.")
        if not self.description.strip():
            raise ValueError("Case description cannot be empty.")

        if len(self.hypotheses) < 2:
            raise ValueError(
                "A case must contain at least two competing hypotheses."
            )

        if not self.evidence:
            raise ValueError(
                "A case must contain at least one evidence item."
            )

        hypothesis_ids = [item.id for item in self.hypotheses]
        if len(hypothesis_ids) != len(set(hypothesis_ids)):
            raise ValueError("Hypothesis IDs must be unique within a case.")

        evidence_ids = [item.id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("Evidence IDs must be unique within a case.")

        if self.ground_truth_hypothesis_id not in hypothesis_ids:
            raise ValueError(
                "Ground truth must reference an existing hypothesis."
            )