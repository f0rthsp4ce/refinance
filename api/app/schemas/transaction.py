"""DTO for Transaction"""

from decimal import Decimal

from app.models.transaction import TransactionStatus
from app.schemas.base import (
    BaseFilterSchema,
    BaseReadSchema,
    BaseUpdateSchema,
    CurrencyDecimal,
)
from app.schemas.entity import EntitySchema
from app.schemas.mixins.tags_filter_mixin import TagsFilterSchemaMixin
from app.schemas.tag import TagSchema
from pydantic import field_validator, model_validator


class TransactionSchema(BaseReadSchema):
    actor_entity_id: int
    actor_entity: EntitySchema
    to_entity_id: int
    to_entity: EntitySchema
    from_entity_id: int
    from_entity: EntitySchema
    amount: CurrencyDecimal
    currency: str
    status: TransactionStatus
    tags: list[TagSchema]


class TransactionCreateSchema(BaseUpdateSchema):
    to_entity_id: int
    from_entity_id: int
    amount: Decimal
    currency: str
    status: TransactionStatus | None = None

    @field_validator("currency")
    def currency_must_be_lowercase(cls, v):
        return v.lower()

    @model_validator(mode="after")
    def check_ids_are_different(self):
        if self.from_entity_id == self.to_entity_id:
            raise ValueError("from_entity_id and to_entity_id must be different")
        return self


class TransactionUpdateSchema(BaseUpdateSchema):
    amount: Decimal | None = None
    currency: str | None = None
    status: TransactionStatus | None = None


class TransactionFiltersSchema(TagsFilterSchemaMixin, BaseFilterSchema):
    entity_id: int | None = None
    actor_entity_id: int | None = None
    to_entity_id: int | None = None
    from_entity_id: int | None = None
    amount_min: Decimal | None = None
    amount_max: Decimal | None = None
    currency: str | None = None
    status: TransactionStatus | None = None
