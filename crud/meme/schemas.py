from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict



class MemeCreate(BaseModel):
    description: Annotated[str, MinLen(2)]
    image_path: Annotated[str, MinLen(0)]


class MemeUpdate(BaseModel):
    description: Annotated[str, MinLen(2)] = None
    image_path: Annotated[str, MinLen(0)] = None