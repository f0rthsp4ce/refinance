"""API routes for Transaction manipulation"""

from app.middlewares.token import get_entity_from_token
from app.models.entity import Entity
from app.schemas.base import PaginationSchema
from app.schemas.transaction import (
    TransactionCreateSchema,
    TransactionFiltersSchema,
    TransactionSchema,
    TransactionUpdateSchema,
)
from app.services.transaction import TransactionService
from fastapi import APIRouter, Depends

transaction_router = APIRouter(prefix="/transactions", tags=["Transactions"])


@transaction_router.post("", response_model=TransactionSchema)
def create_transaction(
    transaction: TransactionCreateSchema,
    transaction_service: TransactionService = Depends(),
    actor_entity: Entity = Depends(get_entity_from_token),
):
    return transaction_service.create(
        transaction, overrides={"actor_entity_id": actor_entity.id}
    )


@transaction_router.get("/{transaction_id}", response_model=TransactionSchema)
def read_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(),
    actor_entity: Entity = Depends(get_entity_from_token),
):
    return transaction_service.get(transaction_id)


@transaction_router.get("", response_model=PaginationSchema[TransactionSchema])
def read_transactions(
    filters: TransactionFiltersSchema = Depends(),
    skip: int = 0,
    limit: int = 100,
    transaction_service: TransactionService = Depends(),
    actor_entity: Entity = Depends(get_entity_from_token),
):
    return transaction_service.get_all(filters, skip, limit)


@transaction_router.patch("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdateSchema,
    transaction_service: TransactionService = Depends(),
    actor_entity: Entity = Depends(get_entity_from_token),
):
    return transaction_service.update(transaction_id, transaction_update)


@transaction_router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(),
    actor_entity: Entity = Depends(get_entity_from_token),
) -> int:
    return transaction_service.delete(transaction_id)
