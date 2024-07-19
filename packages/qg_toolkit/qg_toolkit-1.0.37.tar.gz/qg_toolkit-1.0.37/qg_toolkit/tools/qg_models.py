from typing import Optional, Union
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, field_validator



class Image(BaseModel):
    type: str = Field(..., alias="image_type")
    width: int = Field(..., alias="w")
    height: int = Field(..., alias="h")


