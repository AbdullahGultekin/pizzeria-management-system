"""Tests for validation functions."""

import pytest
from validation import (
    validate_phone_bool, validate_name_bool, validate_address_bool,
    validate_house_number_bool, validate_postcode_bool, sanitize_string
)


def test_validate_phone_valid():
    """Test valid phone numbers."""
    assert validate_phone_bool("0477123456") is True  # Valid Belgian mobile
    assert validate_phone_bool("+32477123456") is True
    assert validate_phone_bool("0477 123 456") is True


def test_validate_phone_invalid():
    """Test invalid phone numbers."""
    assert validate_phone_bool("") is False
    assert validate_phone_bool("abc") is False
    assert validate_phone_bool("123") is False  # Too short


def test_validate_name_valid():
    """Test valid names."""
    assert validate_name_bool("John Doe") is True
    assert validate_name_bool("Jan") is True


def test_validate_name_invalid():
    """Test invalid names."""
    assert validate_name_bool("") is False
    assert validate_name_bool("   ") is False


def test_validate_address_valid():
    """Test valid addresses."""
    assert validate_address_bool("Main Street") is True
    assert validate_address_bool("Hoofdstraat 123") is True


def test_validate_address_invalid():
    """Test invalid addresses."""
    assert validate_address_bool("") is False
    assert validate_address_bool("   ") is False


def test_validate_house_number_valid():
    """Test valid house numbers."""
    assert validate_house_number_bool("123") is True
    assert validate_house_number_bool("123A") is True
    assert validate_house_number_bool("12-14") is True


def test_validate_postcode_valid():
    """Test valid postcodes."""
    assert validate_postcode_bool("2000") is True
    assert validate_postcode_bool("9120") is True


def test_validate_postcode_invalid():
    """Test invalid postcodes."""
    assert validate_postcode_bool("") is False
    assert validate_postcode_bool("abc") is False
    assert validate_postcode_bool("12") is False  # Too short


def test_sanitize_string():
    """Test string sanitization."""
    assert sanitize_string("  test  ") == "test"
    assert sanitize_string("test\nstring") == "test string"
    assert sanitize_string("test\tstring") == "test string"



