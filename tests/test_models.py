"""Tests for PALIMPSEST core data models."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from palimpsest.models import Evidence, Hypothesis, InvestigationCase


@pytest.fixture
def sample_case() -> InvestigationCase:
    """Create a valid fictional investigation for testing."""

    hypotheses = (
        Hypothesis(
            id="H1",
            description="An attacker used the account.",
        ),
        Hypothesis(
            id="H2",
            description="A legitimate automated process used the account.",
        ),
    )

    evidence = (
        Evidence(
            id="E1",
            statement="The account authenticated at 02:14 UTC.",
            source_id="AUTH-LOG-01",
            observed_at=datetime(2026, 10, 1, 2, 14, tzinfo=timezone.utc),
        ),
        Evidence(
            id="E2",
            statement="The account accessed a sensitive file.",
            source_id="FILE-LOG-01",
            observed_at=datetime(2026, 10, 1, 2, 16, tzinfo=timezone.utc),
        ),
    )

    return InvestigationCase(
        id="CASE-001",
        title="The Midnight Access",
        description="Investigate unusual access to a sensitive file.",
        hypotheses=hypotheses,
        evidence=evidence,
        ground_truth_hypothesis_id="H2",
    )


def test_valid_case_is_created(sample_case):
    assert sample_case.id == "CASE-001"
    assert len(sample_case.hypotheses) == 2
    assert len(sample_case.evidence) == 2


def test_ground_truth_references_a_valid_hypothesis(sample_case):
    hypothesis_ids = {h.id for h in sample_case.hypotheses}
    assert sample_case.ground_truth_hypothesis_id in hypothesis_ids


def test_duplicate_hypothesis_ids_are_rejected(sample_case):
    duplicate_hypotheses = (
        sample_case.hypotheses[0],
        sample_case.hypotheses[0],
    )

    with pytest.raises(ValueError, match="Hypothesis IDs must be unique"):
        InvestigationCase(
            id="CASE-002",
            title="Duplicate Hypotheses",
            description="Test duplicate hypothesis IDs.",
            hypotheses=duplicate_hypotheses,
            evidence=sample_case.evidence,
            ground_truth_hypothesis_id="H1",
        )


def test_duplicate_evidence_ids_are_rejected(sample_case):
    duplicate_evidence = (
        sample_case.evidence[0],
        sample_case.evidence[0],
    )

    with pytest.raises(ValueError, match="Evidence IDs must be unique"):
        InvestigationCase(
            id="CASE-003",
            title="Duplicate Evidence",
            description="Test duplicate evidence IDs.",
            hypotheses=sample_case.hypotheses,
            evidence=duplicate_evidence,
            ground_truth_hypothesis_id="H1",
        )


def test_unknown_ground_truth_is_rejected(sample_case):
    with pytest.raises(ValueError, match="Ground truth must reference"):
        InvestigationCase(
            id="CASE-004",
            title="Unknown Ground Truth",
            description="Test an invalid ground-truth reference.",
            hypotheses=sample_case.hypotheses,
            evidence=sample_case.evidence,
            ground_truth_hypothesis_id="H99",
        )


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="must include a timezone"):
        Evidence(
            id="E99",
            statement="An event was recorded.",
            source_id="LOG-99",
            observed_at=datetime(2026, 10, 1, 2, 14),
        )


def test_empty_evidence_statement_is_rejected():
    with pytest.raises(ValueError, match="Evidence statement cannot be empty"):
        Evidence(
            id="E99",
            statement="   ",
            source_id="LOG-99",
            observed_at=datetime.now(timezone.utc),
        )


def test_model_fields_cannot_be_reassigned(sample_case):
    with pytest.raises(FrozenInstanceError):
        sample_case.title = "Modified case"