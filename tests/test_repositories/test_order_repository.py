"""Tests for OrderRepository."""

import pytest
from datetime import datetime
from repositories.order_repository import OrderRepository
from repositories.customer_repository import CustomerRepository


def test_create_order(order_repo, customer_repo, sample_customer_data):
    """Test creating a new order."""
    # Create customer first
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Create order
    nu = datetime.now()
    bestelling_id = order_repo.create(
        klant_id=klant_id,
        datum=nu.strftime('%Y-%m-%d'),
        tijd=nu.strftime('%H:%M'),
        totaal=21.00,
        opmerking="Test order",
        bonnummer="20240001"
    )
    
    assert bestelling_id > 0


def test_get_order_by_id(order_repo, customer_repo, sample_customer_data):
    """Test getting order by ID."""
    # Create customer and order
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    nu = datetime.now()
    bestelling_id = order_repo.create(
        klant_id=klant_id,
        datum=nu.strftime('%Y-%m-%d'),
        tijd=nu.strftime('%H:%M'),
        totaal=21.00,
        opmerking="Test order",
        bonnummer="20240001"
    )
    
    # Get order
    order = order_repo.get_by_id(bestelling_id)
    assert order is not None
    assert order["id"] == bestelling_id
    assert order["klant_id"] == klant_id
    assert order["totaal"] == 21.00


def test_add_order_item(order_repo, customer_repo, sample_customer_data):
    """Test adding items to an order."""
    # Create customer and order
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    nu = datetime.now()
    bestelling_id = order_repo.create(
        klant_id=klant_id,
        datum=nu.strftime('%Y-%m-%d'),
        tijd=nu.strftime('%H:%M'),
        totaal=21.00,
        opmerking="Test order",
        bonnummer="20240001"
    )
    
    # Add item
    item_id = order_repo.add_order_item(
        bestelling_id=bestelling_id,
        categorie="Pizza's",
        product="Margherita",
        aantal=2,
        prijs=10.50,
        extras={"kaas": "extra"}
    )
    
    assert item_id > 0
    
    # Get items
    items = order_repo.get_order_items(bestelling_id)
    assert len(items) == 1
    assert items[0]["product"] == "Margherita"
    assert items[0]["aantal"] == 2


def test_get_orders_by_date(order_repo, customer_repo, sample_customer_data):
    """Test getting orders by date."""
    # Create customer
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    # Create orders for today
    today = datetime.now().strftime('%Y-%m-%d')
    order_repo.create(klant_id, today, "12:00", 10.00, None, "20240001")
    order_repo.create(klant_id, today, "13:00", 20.00, None, "20240002")
    
    # Get orders for today
    orders = order_repo.get_by_date(today)
    assert len(orders) == 2


def test_delete_order(order_repo, customer_repo, sample_customer_data):
    """Test deleting an order."""
    # Create customer and order
    klant_id = customer_repo.create_or_update(
        telefoon=sample_customer_data["telefoon"],
        straat=sample_customer_data["straat"],
        huisnummer=sample_customer_data["huisnummer"],
        plaats=sample_customer_data["plaats"],
        naam=sample_customer_data["naam"]
    )
    
    nu = datetime.now()
    bestelling_id = order_repo.create(
        klant_id=klant_id,
        datum=nu.strftime('%Y-%m-%d'),
        tijd=nu.strftime('%H:%M'),
        totaal=21.00,
        opmerking="Test order",
        bonnummer="20240001"
    )
    
    # Add item
    order_repo.add_order_item(bestelling_id, "Pizza's", "Margherita", 1, 10.50, None)
    
    # Delete order
    order_repo.delete(bestelling_id)
    
    # Verify deleted
    order = order_repo.get_by_id(bestelling_id)
    assert order is None
    
    items = order_repo.get_order_items(bestelling_id)
    assert len(items) == 0



