from pydantic import BaseModel, Field


class CLIModel(BaseModel):
    name: str = Field(..., description='Name of the CLI')
    description: str = Field(..., description='Description of the CLI')
