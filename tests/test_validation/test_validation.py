"""Tests for validation functions."""

import pytest
from validation import (
    validate_phone, validate_name, validate_address,
    validate_house_number, validate_postcode, sanitize_string
)


def test_validate_phone_valid():
    """Test valid phone numbers."""
    assert validate_phone("0123456789") is True
    assert validate_phone("+32123456789") is True
    assert validate_phone("0123 456 789") is True


def test_validate_phone_invalid():
    """Test invalid phone numbers."""
    assert validate_phone("") is False
    assert validate_phone("abc") is False
    assert validate_phone("123") is False  # Too short


def test_validate_name_valid():
    """Test valid names."""
    assert validate_name("John Doe") is True
    assert validate_name("Jan") is True


def test_validate_name_invalid():
    """Test invalid names."""
    assert validate_name("") is False
    assert validate_name("   ") is False


def test_validate_address_valid():
    """Test valid addresses."""
    assert validate_address("Main Street") is True
    assert validate_address("Hoofdstraat 123") is True


def test_validate_address_invalid():
    """Test invalid addresses."""
    assert validate_address("") is False
    assert validate_address("   ") is False


def test_validate_house_number_valid():
    """Test valid house numbers."""
    assert validate_house_number("123") is True
    assert validate_house_number("123A") is True
    assert validate_house_number("12-14") is True


def test_validate_postcode_valid():
    """Test valid postcodes."""
    assert validate_postcode("2000") is True
    assert validate_postcode("9120") is True


def test_validate_postcode_invalid():
    """Test invalid postcodes."""
    assert validate_postcode("") is False
    assert validate_postcode("abc") is False
    assert validate_postcode("12") is False  # Too short


def test_sanitize_string():
    """Test string sanitization."""
    assert sanitize_string("  test  ") == "test"
    assert sanitize_string("test\nstring") == "test string"
    assert sanitize_string("test\tstring") == "test string"



