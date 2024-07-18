from sqlalchemy import CursorResult, Row, Table, insert, select, update
from sqlalchemy.orm import Session

from ._models import SeedBinding, SeederElement


class SeederOperator:
    def __init__(self, element: SeederElement, table: Table, binding: SeedBinding = None):
        self.__element = element
        self.__table = table
        self.__binding = binding

    def lookup(self, keys: list[str], session: Session) -> list[Row]:
        stmt = select(
            self.__table,
        ).filter_by(
            **{key: self.__element.columns[key] for key in keys},
        )

        if self.__binding is not None:
            stmt = stmt.filter_by(**{self.__binding.foreign_key: self.__binding.value})

        rows = []

        for row in session.execute(stmt):
            rows.append(row)

        return rows

    def create(self, session: Session) -> CursorResult:
        stmt = insert(
            self.__table,
        ).values(
            **self.__element.columns,
        )

        if self.__binding is not None:
            stmt = stmt.values(**{self.__binding.foreign_key: self.__binding.value})

        return session.execute(stmt)

    def update(self, primary_key: int, session: Session) -> CursorResult:
        primary_key_name = self.__table.primary_key.columns[0].name

        stmt = update(
            self.__table,
        ).filter_by(
            **{primary_key_name: primary_key},
        ).values(
            **self.__element.columns,
        )

        if self.__binding is not None:
            stmt = stmt.values(**{self.__binding.foreign_key: self.__binding.value})

        return session.execute(stmt)
