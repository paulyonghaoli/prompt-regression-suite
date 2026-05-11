import pytest
from scoring.consistency import compute_consistency_score

def test_identical_outputs():
    outputs = ["The sky is blue", "The sky is blue", "The sky is blue"]
    score = compute_consistency_score(outputs)
    assert score == pytest.approx(1.0, abs=0.1)

def test_different_outputs():
    outputs = ["The sky is blue", "The grass is green", "Fire is hot"]
    score = compute_consistency_score(outputs)
    assert score < 0.5

def test_single_output():
    outputs = ["Single"]
    score = compute_consistency_score(outputs)
    assert score == 1.0