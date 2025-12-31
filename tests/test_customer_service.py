"""Tests for customer service."""
import pytest
from sqlalchemy.orm import Session

from src.services.customer_service import CustomerService


def test_create_customer(db_session: Session) -> None:
    """Test creating a new customer."""
    service = CustomerService(db_session)
    
    customer = service.create_customer(
        name="Test Customer",
        area="Test Area",
        mobile="1234567890",
        subscription="Basic",
        custom_rate=500.0,
    )
    
    assert customer["name"] == "Test Customer"
    assert customer["area"] == "Test Area"
    assert customer["subscription"] == "Basic"
    assert customer["custom_rate"] == 500.0
    assert customer["status"] == "active"


def test_create_duplicate_customer(db_session: Session) -> None:
    """Test creating a duplicate customer raises error."""
    service = CustomerService(db_session)
    
    service.create_customer(name="Test Customer")
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_customer(name="Test Customer")


def test_get_all_customers(db_session: Session) -> None:
    """Test getting all customers."""
    service = CustomerService(db_session)
    
    service.create_customer(name="Customer 1")
    service.create_customer(name="Customer 2")
    
    customers = service.get_all_customers(active_only=True)
    
    assert len(customers) == 2
    assert customers[0]["name"] == "Customer 1"
    assert customers[1]["name"] == "Customer 2"


def test_update_customer(db_session: Session) -> None:
    """Test updating customer details."""
    service = CustomerService(db_session)
    
    service.create_customer(name="Test Customer", area="Old Area")
    
    updated = service.update_customer(
        name="Test Customer",
        area="New Area",
        mobile="9876543210",
    )
    
    assert updated["area"] == "New Area"
    assert updated["mobile"] == "9876543210"


def test_deactivate_customer(db_session: Session) -> None:
    """Test deactivating a customer."""
    service = CustomerService(db_session)
    
    service.create_customer(name="Test Customer")
    service.deactivate_customer("Test Customer")
    
    active = service.get_all_customers(active_only=True)
    inactive = service.get_inactive_customers()
    
    assert len(active) == 0
    assert len(inactive) == 1
    assert inactive[0]["name"] == "Test Customer"


def test_reactivate_customer(db_session: Session) -> None:
    """Test reactivating a customer."""
    service = CustomerService(db_session)
    
    service.create_customer(name="Test Customer")
    service.deactivate_customer("Test Customer")
    service.reactivate_customer("Test Customer")
    
    active = service.get_all_customers(active_only=True)
    
    assert len(active) == 1
    assert active[0]["name"] == "Test Customer"
