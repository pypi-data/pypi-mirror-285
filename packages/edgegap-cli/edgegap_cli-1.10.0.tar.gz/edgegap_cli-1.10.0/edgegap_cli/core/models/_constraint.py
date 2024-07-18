from typing import Annotated

from pydantic.types import StringConstraints

no_space_to_lower_str = Annotated[str, StringConstraints(strip_whitespace=True, to_lower=True)]
