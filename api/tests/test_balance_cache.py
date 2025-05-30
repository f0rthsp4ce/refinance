from fastapi import status
from fastapi.testclient import TestClient


class TestBalanceServiceCache:
    """Test cache functionality in BalanceService"""

    def test_cache_functionality(self, test_app: TestClient, token_factory, token):
        # Create entities
        response = test_app.post(
            "/entities", json={"name": "Entity A"}, headers={"x-token": token}
        )
        entity_a_id = response.json()["id"]
        token_a = token_factory(entity_a_id)

        response = test_app.post(
            "/entities", json={"name": "Entity B"}, headers={"x-token": token}
        )
        entity_b_id = response.json()["id"]
        token_b = token_factory(entity_b_id)

        response = test_app.post(
            "/entities", json={"name": "Entity C"}, headers={"x-token": token}
        )
        entity_c_id = response.json()["id"]
        token_c = token_factory(entity_c_id)

        # Create transactions between entities using the new status enum
        transactions = [
            {
                "from_entity_id": entity_a_id,
                "to_entity_id": entity_b_id,
                "amount": "100.00",
                "currency": "usd",
                "status": "completed",
            },
            {
                "from_entity_id": entity_a_id,
                "to_entity_id": entity_c_id,
                "amount": "200.00",
                "currency": "usd",
                "status": "completed",
            },
            {
                "from_entity_id": entity_b_id,
                "to_entity_id": entity_c_id,
                "amount": "150.00",
                "currency": "usd",
                "status": "completed",
            },
        ]

        for transaction_data in transactions:
            response = test_app.post(
                "/transactions/",
                json=transaction_data,
                headers={"x-token": token_factory(transaction_data["from_entity_id"])},
            )
            assert response.status_code == status.HTTP_200_OK

        # Get initial balances using the cached method
        response = test_app.get(
            f"/balances/{entity_a_id}", headers={"x-token": token_a}
        )
        balance_a_1 = response.json()
        response = test_app.get(
            f"/balances/{entity_b_id}", headers={"x-token": token_b}
        )
        balance_b_1 = response.json()
        response = test_app.get(
            f"/balances/{entity_c_id}", headers={"x-token": token_c}
        )
        balance_c_1 = response.json()

        # Expected balances after transactions with updated keys
        expected_balance_a = {"completed": {"usd": "-300.00"}, "draft": {}}
        expected_balance_b = {"completed": {"usd": "-50.00"}, "draft": {}}
        expected_balance_c = {"completed": {"usd": "350.00"}, "draft": {}}

        assert balance_a_1 == expected_balance_a
        assert balance_b_1 == expected_balance_b
        assert balance_c_1 == expected_balance_c

        # Ensure that cached balances remain unchanged
        response = test_app.get(
            f"/balances/{entity_a_id}", headers={"x-token": token_a}
        )
        balance_a_2 = response.json()
        response = test_app.get(
            f"/balances/{entity_b_id}", headers={"x-token": token_b}
        )
        balance_b_2 = response.json()
        response = test_app.get(
            f"/balances/{entity_c_id}", headers={"x-token": token_c}
        )
        balance_c_2 = response.json()

        assert balance_a_2 == balance_a_1
        assert balance_b_2 == balance_b_1
        assert balance_c_2 == balance_c_1

        # Invalidate the cache by creating a new transaction with status "draft"
        response = test_app.post(
            "/transactions/",
            json={
                "from_entity_id": entity_a_id,
                "to_entity_id": entity_b_id,
                "amount": 100,
                "currency": "eth",
                "status": "draft",
            },
            headers={"x-token": token_factory(entity_a_id)},
        )
        assert response.status_code == status.HTTP_200_OK
        tx_id = response.json()["id"]

        test_app.delete(
            f"/transactions/{tx_id}",
            headers={"x-token": token_a},
        )

        # Verify that balances remain as expected after cache invalidation
        response = test_app.get(
            f"/balances/{entity_a_id}", headers={"x-token": token_a}
        )
        balance_a_3 = response.json()
        response = test_app.get(
            f"/balances/{entity_b_id}", headers={"x-token": token_b}
        )
        balance_b_3 = response.json()
        response = test_app.get(
            f"/balances/{entity_c_id}", headers={"x-token": token_c}
        )
        balance_c_3 = response.json()

        assert balance_a_3 == expected_balance_a
        assert balance_b_3 == expected_balance_b
        assert balance_c_3 == expected_balance_c
