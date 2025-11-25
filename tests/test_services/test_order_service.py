"""Tests for OrderService."""

import pytest
from unittest.mock import patch
from services.order_service import OrderService
from exceptions import ValidationError


@patch('services.order_service.boek_voorraad_verbruik')
def test_create_order_success(mock_boek_voorraad, order_service, customer_service, sample_customer_data, sample_order_items):
    """Test successfully creating an order."""
    # Create customer first
    customer_service.create_or_update_customer(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Create order
    success, bonnummer = order_service.create_order(
        klant_telefoon=sample_customer_data["telefoon"],
        order_items=sample_order_items,
        opmerking="Test order"
    )
    
    assert success is True
    assert bonnummer is not None


def test_create_order_invalid_phone(order_service, sample_order_items):
    """Test creating order with invalid phone number."""
    with pytest.raises(ValidationError):
        order_service.create_order(
            klant_telefoon="",
            order_items=sample_order_items
        )


def test_create_order_empty_items(order_service, customer_service, sample_customer_data):
    """Test creating order with no items."""
    customer_service.create_or_update_customer(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    with pytest.raises(ValidationError):
        order_service.create_order(
            klant_telefoon=sample_customer_data["telefoon"],
            order_items=[]
        )


def test_create_order_customer_not_found(order_service, sample_order_items):
    """Test creating order for non-existent customer."""
    with pytest.raises(ValidationError):
        order_service.create_order(
            klant_telefoon="9999999999",
            order_items=sample_order_items
        )



