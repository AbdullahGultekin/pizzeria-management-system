"""Tests for CustomerService."""

import pytest
from services.customer_service import CustomerService
from exceptions import ValidationError


def test_find_customer_not_found(customer_service):
    """Test finding non-existent customer."""
    result = customer_service.find_customer("9999999999")
    assert result is None


def test_create_customer(customer_service, sample_customer_data):
    """Test creating a customer through service."""
    klant_id = customer_service.create_or_update_customer(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    assert klant_id > 0


def test_search_customers(customer_service, sample_customer_data):
    """Test searching customers."""
    # Create customers
    customer_service.create_or_update_customer("0123456789", "Straat1", "1", "Plaats1", "Klant1")
    customer_service.create_or_update_customer("0123456790", "Straat2", "2", "Plaats2", "Klant2")
    
    # Search
    results = customer_service.search_customers("%01234567%")
    assert len(results) == 2


def test_update_customer_statistics(customer_service, sample_customer_data):
    """Test updating customer statistics."""
    klant_id = customer_service.create_or_update_customer(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Should not raise exception
    customer_service.update_customer_statistics(klant_id)



