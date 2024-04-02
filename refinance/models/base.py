"""Base for all ORM models"""

from typing import Any, Optional

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    # do not create separate table for this class
    __abstract__ = True

    # everything should have an id and a comment
    id: Mapped[int] = mapped_column(primary_key=True)
    comment: Mapped[Optional[str]]

    def __repr__(self) -> str:
        """Automatically generate beautiful __repr__ of a database object (chatgpt4 generated snippet)"""
        model_name = self.__class__.__name__
        attr_strs = []
        for attr, column in inspect(self.__class__).columns.items():  # type: ignore[union-attr]
            value = getattr(self, attr)
            attr_strs.append(f"{attr}={value!r}")  # !r calls repr() on the value to get a nice string representation
        attr_str = ", ".join(attr_strs)
        return f"<{model_name}({attr_str})>"

    def model_dump(self) -> dict[str, Any]:
        """Return the dictionary representation of the model."""
        d = self.__dict__.copy()
        d.pop("_sa_instance_state", None)
        return d
