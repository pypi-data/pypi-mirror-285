from typing import Callable

from pydantic import BaseModel, Field

from ._constraint import no_space_to_lower_str


class ViewModel(BaseModel):
    name: no_space_to_lower_str = Field(..., description='Name of the view')
    description: str = Field(..., description='Description of the view')
    func: Callable = Field(..., description='The function of the view')
    confirm_message: str | None = Field(default=None, description='Enable a confirmation message')
    wait_on_exit: bool = Field(default=True, description='Wait when exiting the view')
