from typing import Any

from pydantic import BaseModel, Field

from ._enum import OperationEnum


class SeedBinding(BaseModel):
    value: Any | None = Field(None, description="The value to insert from the primary to the foreign")
    foreign_key: str = Field(..., description="The foreign key to insert the primary key")

    def __str__(self) -> str:
        return f"{self.foreign_key}->{self.value}"


class SeederElement(BaseModel):
    name: str = Field(..., description="The name of the seeder element")
    columns: dict[str, Any] = Field(..., description="The columns and their values")
    sub_elements: list['SeederModel'] = Field(..., description="The sub elements")

    def __str__(self) -> str:
        return f"Element [{self.name}] - {len(self.columns)} Columns - {len(self.sub_elements)} Sub Elements"


class SeederModel(BaseModel):
    name: str = Field(..., description="The name of the seeder.")
    table: str = Field(..., description="Table name")
    operation: OperationEnum = Field(..., description="Operation name")
    lookup_keys: list[str] = Field(..., description="Lookup keys")
    binding: SeedBinding | None = Field(None, description="Relation Binding naming (column ID)")
    elements: list[SeederElement] = Field(..., description="List of Elements to seed")

    def __str__(self) -> str:
        return (
            f"Seed [{self.name}] - "
            f"Table [{self.table}] - "
            f"Binding [{self.binding}] - "
            f"Operation [{self.operation.value}] on {len(self.elements)} Elements"
        )
