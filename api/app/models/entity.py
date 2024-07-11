"""Entity model. Main unit of refinance system. May receive or send money."""

from typing import List

from app.models.base import BaseModel
from app.models.tag import Tag
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

entities_tags = Table(
    "entities_tags",
    BaseModel.metadata,
    Column("entity_id", ForeignKey("entities.id")),
    Column("tag_id", ForeignKey("tags.id")),
)


class Entity(BaseModel):
    __tablename__ = "entities"

    name: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(default=True)
    tags: Mapped[List[Tag]] = relationship(secondary=entities_tags)

    # authentication
    telegram_id: Mapped[int] = mapped_column(nullable=True, unique=True)
