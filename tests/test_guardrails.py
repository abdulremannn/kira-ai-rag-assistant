import pytest

from app.guardrails import InvalidInput, is_relevant, validate_question


def test_validate_question_strips_and_passes():
    assert validate_question("  hello  ", 500) == "hello"


def test_validate_question_rejects_empty():
    with pytest.raises(InvalidInput):
        validate_question("   ", 500)


def test_validate_question_rejects_too_long():
    with pytest.raises(InvalidInput):
        validate_question("x" * 501, 500)


def test_validate_question_rejects_control_chars():
    with pytest.raises(InvalidInput):
        validate_question("hello\x00world", 500)


def test_is_relevant_above_threshold():
    assert is_relevant(0.5, 0.3) is True


def test_is_relevant_below_threshold():
    assert is_relevant(0.2, 0.3) is False


def test_is_relevant_at_threshold_boundary():
    assert is_relevant(0.3, 0.3) is True
