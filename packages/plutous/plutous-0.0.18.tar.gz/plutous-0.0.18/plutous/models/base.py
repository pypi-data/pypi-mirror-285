import datetime as dt
import re

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as _Enum
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class BaseMixin:
    __name__: str

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP,
        default=lambda: dt.datetime.now(dt.timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        default=lambda: dt.datetime.now(dt.timezone.utc),
        onupdate=lambda: dt.datetime.now(dt.timezone.utc),
    )

    def dict(self) -> dict:
        return {
            key: attr
            for key, attr in self.__dict__.items()
            if key != "_sa_instance_state"
        }

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return re.sub("(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    @declared_attr.directive
    def __table_args__(cls) -> tuple:
        return (
            Index(
                f"ix_{cls.__tablename__}_created_at",
                "created_at",
            ),
            Index(
                f"ix_{cls.__tablename__}_updated_at",
                "updated_at",
            ),
        )

    def __repr__(self):
        columns = self.__dict__.keys()
        column_values = ", ".join(
            f"{col}={getattr(self, col)!r}"
            for col in columns
            if col != "_sa_instance_state"
        )
        return f"{self.__class__.__name__}({column_values})"


class Enum(_Enum):
    schema = None

    def __init__(self, *args, **kwargs):
        schema = kwargs.pop("schema", None)
        if schema is not None:
            self.schema = schema
        super().__init__(schema=self.schema, *args, **kwargs)
