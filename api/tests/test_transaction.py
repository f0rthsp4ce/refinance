from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="class")
def entity_one(test_app: TestClient, token):
    response = test_app.post(
        "/entities", json={"name": "User One 1"}, headers={"x-token": token}
    )
    assert response.status_code == 200
    data = response.json()
    return data["id"]


@pytest.fixture(scope="class")
def entity_two(test_app: TestClient, token):
    response = test_app.post(
        "/entities", json={"name": "User Two 2"}, headers={"x-token": token}
    )
    assert response.status_code == 200
    data = response.json()
    return data["id"]


@pytest.fixture
def create_transaction(test_app: TestClient, entity_one, entity_two, token):
    response = test_app.post(
        "/transactions",
        json={
            "from_entity_id": entity_one,
            "to_entity_id": entity_two,
            "amount": "150.00",
            "currency": "usd",
        },
        headers={"x-token": token},
    )
    assert response.status_code == 200
    return response


class TestTransactionEndpoints:
    """Test API endpoints for transactions"""

    def test_create_transaction(
        self, test_app: TestClient, entity_one, entity_two, token
    ):
        # Create a new transaction
        response = test_app.post(
            "/transactions",
            json={
                "from_entity_id": entity_one,
                "to_entity_id": entity_two,
                "amount": "200.00",
                "currency": "usd",
            },
            headers={"x-token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["from_entity_id"] == entity_one
        assert data["to_entity_id"] == entity_two
        assert Decimal(data["amount"]) == Decimal("200.00")
        assert data["currency"] == "usd"

    def test_get_transaction(self, test_app: TestClient, create_transaction, token):
        # Get transaction, check all create details match
        transaction_id = create_transaction.json()["id"]
        response = test_app.get(
            f"/transactions/{transaction_id}", headers={"x-token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == transaction_id

    def test_cannot_unconfirm_confirmed_transaction(
        self, test_app: TestClient, entity_one, entity_two, token
    ):
        """
        Ensure that once a transaction is confirmed, it cannot be updated to unconfirmed.
        Adjust this test as needed if your update endpoint or behavior differs.
        """
        # First, create a transaction that is confirmed
        create_response = test_app.post(
            "/transactions",
            json={
                "from_entity_id": entity_one,
                "to_entity_id": entity_two,
                "amount": "300.00",
                "currency": "usd",
                "confirmed": True,
            },
            headers={"x-token": token},
        )
        assert create_response.status_code == 200
        tx_data = create_response.json()
        tx_id = tx_data["id"]
        assert tx_data["confirmed"] is True

        # Try to unconfirm the transaction
        update_response = test_app.patch(
            f"/transactions/{tx_id}",
            json={"confirmed": False},
            headers={"x-token": token},
        )
        # Depending on your API, you might expect a 400, 403, 409, etc.
        # The key part is that it should NOT be successful (200).
        assert update_response.status_code == 418, "Expected 418"

        # Double-check the transaction is still confirmed
        get_response = test_app.get(
            f"/transactions/{tx_id}",
            headers={"x-token": token},
        )
        assert get_response.status_code == 200
        updated_data = get_response.json()
        assert (
            updated_data["confirmed"] is True
        ), "Transaction should still be confirmed"


@pytest.fixture
def multiple_transactions(test_app: TestClient, entity_one, entity_two, token):
    """Create multiple transactions to test filtering."""
    transactions = [
        {
            "from_entity_id": entity_one,
            "to_entity_id": entity_two,
            "amount": "50.00",
            "currency": "usd",
            "confirmed": True,
        },
        {
            "from_entity_id": entity_two,
            "to_entity_id": entity_one,
            "amount": "75.00",
            "currency": "eur",
            "confirmed": False,
        },
        {
            "from_entity_id": entity_one,
            "to_entity_id": entity_two,
            "amount": "150.00",
            "currency": "usd",
            "confirmed": True,
        },
        {
            "from_entity_id": entity_two,
            "to_entity_id": entity_one,
            "amount": "200.00",
            "currency": "usd",
            "confirmed": False,
        },
    ]
    for transaction in transactions:
        response = test_app.post(
            "/transactions", json=transaction, headers={"x-token": token}
        )
        assert response.status_code == 200


class TestTransactionFiltering:
    """Test filtering logic for transaction endpoints"""

    def test_filter_by_currency(
        self, test_app: TestClient, multiple_transactions, token
    ):
        # Filter transactions by currency USD
        response = test_app.get(
            "/transactions", params={"currency": "usd"}, headers={"x-token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            len(data) == 4
        )  # Assuming the response model includes a list of transactions

    def test_filter_by_amount_range(
        self, test_app: TestClient, multiple_transactions, token
    ):
        # Filter transactions where amount is between 100 and 300
        response = test_app.get(
            "/transactions",
            params={"amount_min": "100", "amount_max": "300"},
            headers={"x-token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Check the number of transactions returned

    def test_filter_by_confirmation_status(
        self, test_app: TestClient, multiple_transactions, token
    ):
        # Filter transactions by confirmed status
        response = test_app.get(
            "/transactions", params={"confirmed": True}, headers={"x-token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Transactions that are confirmed

    def test_filter_by_from_entity_id(
        self, test_app: TestClient, multiple_transactions, entity_one, token
    ):
        # Filter transactions by from_entity_id
        response = test_app.get(
            "/transactions",
            params={"from_entity_id": entity_one},
            headers={"x-token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Transactions originating from entity_one

    def test_filter_by_to_entity_id(
        self, test_app: TestClient, multiple_transactions, entity_two, token
    ):
        # Filter transactions by to_entity_id
        response = test_app.get(
            "/transactions",
            params={"to_entity_id": entity_two},
            headers={"x-token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4  # Transactions directed to entity_two

    def test_filter_by_entity_id(
        self, test_app: TestClient, multiple_transactions, entity_one, entity_two, token
    ):
        # Filter transactions by entity_id
        response = test_app.get(
            "/transactions",
            params={"entity_id": entity_one},
            headers={"x-token": token},
        )
        assert response.status_code == 200
        data = response.json()
        assert (
            len(data) == 4
        )  # Transactions either directed to or originated from entity_one
