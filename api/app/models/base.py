"""Base for all ORM models"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    __abstract__ = True


class BaseModel(Base):
    # do not create separate table for this class
    __abstract__ = True
    # force AUTOINCREMENT statement for sqlite, as this dialect omits it by default, but we do need sqlite_sequence table for correct seeding.
    __table_args__ = {"sqlite_autoincrement": True}

    # everything should have an id and a comment
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)

    def __repr__(self):
        """Automatically generate beautiful __repr__ of a database object (chatgpt4 generated snippet)"""
        model_name = self.__class__.__name__
        attr_strs = []
        for attr, column in inspect(self.__class__).columns.items():
            value = getattr(self, attr)
            attr_strs.append(
                f"{attr}={value!r}"
            )  # !r calls repr() on the value to get a nice string representation
        attr_str = ", ".join(attr_strs)
        return f"<{model_name}({attr_str})>"
