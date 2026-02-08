"""Tests for greeting processor."""

from src.processor import MAX_NAME_LENGTH, process_greeting


def test_basic_greeting():
    assert process_greeting("World") == "Hello World!"


def test_strips_whitespace():
    assert process_greeting("  Alice  ") == "Hello Alice!"


def test_empty_string():
    assert process_greeting("") == "Hello stranger!"


def test_whitespace_only():
    assert process_greeting("   ") == "Hello stranger!"


def test_truncates_long_name():
    long_name = "A" * 300
    result = process_greeting(long_name)
    assert result == f"Hello {'A' * MAX_NAME_LENGTH}...!"
    assert len(result) < len(long_name)


def test_exact_max_length():
    name = "B" * MAX_NAME_LENGTH
    assert process_greeting(name) == f"Hello {name}!"


def test_one_over_max_length():
    name = "C" * (MAX_NAME_LENGTH + 1)
    assert process_greeting(name) == f"Hello {'C' * MAX_NAME_LENGTH}...!"


def test_special_characters():
    assert process_greeting("O'Brien") == "Hello O'Brien!"


def test_unicode_name():
    assert process_greeting("世界") == "Hello 世界!"
