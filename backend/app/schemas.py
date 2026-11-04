import datetime as dt
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints
from pydantic.alias_generators import to_camel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Color = Annotated[str, StringConstraints(max_length=20)]

class CamelModel(BaseModel):
    # Python code uses snake_case; JSON uses camelCase (what the React app expects)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class HabitCreate(CamelModel):
    name: Name
    color: Color | None = None

class HabitUpdate(CamelModel):
    name: Name | None = None
    color: Color | None = None
    archived: bool | None = None

class HabitOut(CamelModel):
    id: int
    name: str
    color: str | None
    current_streak: int
    longest_streak: int
    done_today: bool