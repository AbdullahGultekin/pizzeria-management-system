"""Tests for CustomerRepository."""

import pytest
from repositories.customer_repository import CustomerRepository


def test_find_by_phone_not_found(customer_repo):
    """Test finding non-existent customer."""
    result = customer_repo.find_by_phone("9999999999")
    assert result is None


def test_create_customer(customer_repo, sample_customer_data):
    """Test creating a new customer."""
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    assert klant_id > 0


def test_find_by_phone(customer_repo, sample_customer_data):
    """Test finding customer by phone."""
    # Create customer first
    customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Find it
    result = customer_repo.find_by_phone(sample_customer_data["telefoon"])
    assert result is not None
    assert result["telefoon"] == sample_customer_data["telefoon"]
    assert result["naam"] == sample_customer_data["naam"]


def test_update_customer(customer_repo, sample_customer_data):
    """Test updating existing customer."""
    # Create customer
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Update customer
    customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat="Nieuwe Straat",
        huisnummer="456",
        plaats="Nieuwe Stad",
        naam="Nieuwe Naam"
    )
    
    # Verify update
    result = customer_repo.find_by_phone(sample_customer_data["telefoon"])
    assert result["straat"] == "Nieuwe Straat"
    assert result["naam"] == "Nieuwe Naam"
    assert result["id"] == klant_id  # Same ID


def test_get_by_id(customer_repo, sample_customer_data):
    """Test getting customer by ID."""
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    result = customer_repo.get_by_id(klant_id)
    assert result is not None
    assert result["id"] == klant_id
    assert result["telefoon"] == sample_customer_data["telefoon"]


def test_find_by_phone_like(customer_repo, sample_customer_data):
    """Test finding customers by phone pattern."""
    # Create a few customers
    customer_repo.create_or_update("0123456789", "Straat1", "1", "Plaats1", "Klant1")
    customer_repo.create_or_update("0123456790", "Straat2", "2", "Plaats2", "Klant2")
    customer_repo.create_or_update("0987654321", "Straat3", "3", "Plaats3", "Klant3")
    
    # Search for pattern
    results = customer_repo.find_by_phone_like("%01234567%")
    assert len(results) == 2
    assert all("01234567" in r["telefoon"] for r in results)



