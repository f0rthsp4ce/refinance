"""Tests for Balance API and Transaction confirmation"""

from decimal import Decimal

from fastapi import status
from fastapi.testclient import TestClient


class TestBalanceEndpoints:
    """Test API endpoints for Balance"""

    def test_entity_transactions_balance(self, test_app: TestClient):
        # Create entities
        response = test_app.post("/entities/", json={"name": "Entity A"})
        entity_a_id = response.json()["id"]
        response = test_app.post("/entities/", json={"name": "Entity B"})
        entity_b_id = response.json()["id"]

        # Create a transaction from Entity A to Entity B
        transaction_data = {
            "from_entity_id": entity_a_id,
            "to_entity_id": entity_b_id,
            "amount": "100.00",
            "currency": "usd",
        }
        response = test_app.post("/transactions/", json=transaction_data)
        transaction_id = response.json()["id"]

        # Check initial balance for Entity A and Entity B
        response = test_app.get(f"/balances/{entity_a_id}")
        assert response.json()["confirmed"] == {}
        assert Decimal(response.json()["non_confirmed"]["usd"]) == Decimal("-100")
        response = test_app.get(f"/balances/{entity_b_id}")
        assert response.json()["confirmed"] == {}
        assert Decimal(response.json()["non_confirmed"]["usd"]) == Decimal("100")

        # Confirm the transaction
        response = test_app.patch(
            f"/transactions/{transaction_id}", json={"confirmed": True}
        )
        assert response.status_code == status.HTTP_200_OK

        # Check balance after confirming the transaction
        response = test_app.get(f"/balances/{entity_a_id}")
        balance_a = Decimal(response.json()["confirmed"]["usd"])
        assert balance_a == Decimal("-100")
        response = test_app.get(f"/balances/{entity_b_id}")
        balance_b = Decimal(response.json()["confirmed"]["usd"])
        assert balance_b == Decimal("100")