from pydantic import BaseModel, Field

from ._constraint import no_space_to_lower_str


class NamespaceModel(BaseModel):
    name: no_space_to_lower_str = Field(..., description='The name of the namespace')
    description: str = Field(..., description='Description of the namespace')
